from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)
from config import TELEGRAM_TOKEN
from ask_gemini import ask_gemini
from pdf_reader import extract_text_from_pdf

import os

# States
FACULTY, DEPARTMENT, LEVEL, COURSE = range(4)

# --- Faculties and Departments ---
FACULTIES = {
    "1": ("Faculty of Computing and Mathematical Sciences", [
        "1. Computer Science",
        "2. Mathematics",
        "3. Statistics"
    ]),
    "2": ("Faculty of Engineering", [
        "1. Civil Engineering",
        "2. Electrical Engineering",
        "3. Mechanical Engineering"
    ]),
    "3": ("Faculty of Agriculture", [
        "1. Crop Science",
        "2. Soil Science",
        "3. Agricultural Economics"
    ]),
    "4": ("Faculty of Sciences", [
        "1. Biochemistry",
        "2. Microbiology",
        "3. Physics"
    ]),
    "5": ("Faculty of Education", [
        "1. Science Education",
        "2. Educational Psychology",
        "3. Technical Education"
    ]),
}

LEVELS = {
    "1": "100 Level",
    "2": "200 Level",
    "3": "300 Level",
    "4": "400 Level"
}

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faculties_list = "\n".join([f"{k}. {v[0]}" for k, v in FACULTIES.items()])
    await update.message.reply_text(
        "👋 Assalamu Alaikum!\n\n"
        "I'm *AskProfAI*, your academic assistant at ADUSTECH.\n\n"
        "Let’s start with your *Faculty*. Choose from the available options below by typing the number:\n\n"
        f"{faculties_list}",
        parse_mode="Markdown"
    )
    return FACULTY

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ You can:\n"
        "- Type /start to select your faculty, department, level, and course.\n"
        "- Then ask any question about your course.\n"
        "- Or type /about to know more about me.\n"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *AskProfAI* is an AI-powered Telegram bot built by Muhammad Niimatullah.\n"
        "It helps students at ADUSTECH study smarter using Google Gemini.\n\n"
        "📚 Powered by local syllabus content.\n"
        "💡 Built with ❤️ and Python.",
        parse_mode="Markdown"
    )

# --- Conversation flow ---
async def faculty_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if choice not in FACULTIES:
        await update.message.reply_text("⚠️ Invalid choice. Please type a valid number for faculty.")
        return FACULTY

    faculty_name, departments = FACULTIES[choice]
    context.user_data["faculty"] = faculty_name

    dept_list = "\n".join(departments)
    await update.message.reply_text(
        f"✅ Faculty selected: *{faculty_name}*\n\n"
        "Now choose your *Department* by typing the number:\n\n"
        f"{dept_list}",
        parse_mode="Markdown"
    )
    return DEPARTMENT

async def department_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    faculty = context.user_data.get("faculty")

    # Get departments of chosen faculty
    for key, (fac, departments) in FACULTIES.items():
        if fac == faculty:
            if choice not in [d.split(".")[0] for d in departments]:
                await update.message.reply_text("⚠️ Invalid choice. Please type a valid number for department.")
                return DEPARTMENT
            dept_name = [d for d in departments if d.startswith(choice)][0].split(". ")[1]
            context.user_data["department"] = dept_name

    levels_list = "\n".join([f"{k}. {v}" for k, v in LEVELS.items()])
    await update.message.reply_text(
        f"✅ Department selected: *{context.user_data['department']}*\n\n"
        "Now choose your *Level* by typing the number:\n\n"
        f"{levels_list}",
        parse_mode="Markdown"
    )
    return LEVEL

async def level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if choice not in LEVELS:
        await update.message.reply_text("⚠️ Invalid choice. Please type a valid number for level.")
        return LEVEL

    context.user_data["level"] = LEVELS[choice]

    courses = [f for f in os.listdir("pdfs") if f.endswith(".pdf")]
    if not courses:
        courses = ["No courses found (add PDFs to /pdfs folder)"]

    course_list = "\n".join([f"{i+1}. {c}" for i, c in enumerate(courses)])
    await update.message.reply_text(
        f"✅ Level selected: *{context.user_data['level']}*\n\n"
        "Now choose your *Course* by typing the number:\n\n"
        f"{course_list}",
        parse_mode="Markdown"
    )
    context.user_data["courses"] = courses
    return COURSE

async def course_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    courses = context.user_data.get("courses", [])

    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(courses):
        await update.message.reply_text("⚠️ Invalid choice. Please type a valid number for course.")
        return COURSE

    course_file = courses[int(choice)-1]
    context.user_data["course"] = course_file

    await update.message.reply_text(
        f"✅ Course selected: *{course_file}*\n\n"
        "You’re all set! 🎉\nNow ask me any question about this course.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# --- Handle questions ---
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    course_file = context.user_data.get("course")
    if not course_file:
        await update.message.reply_text("⚠️ Please select a course first with /start")
        return

    try:
        pdf_text = extract_text_from_pdf(course_file)
    except Exception as e:
        await update.message.reply_text(f"❌ Could not load course material: {e}")
        return

    await update.message.reply_text("⏳ Asking Gemini... please wait.")
    answer = ask_gemini(update.message.text, pdf_text)
    await update.message.reply_text(f"📘 {answer}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Setup canceled. Type /start to begin again.")
    return ConversationHandler.END

# --- Main ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))

    # Setup flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, faculty_handler)],
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, department_handler)],
            LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_handler)],
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    # Questions after setup
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    print("✅ AskProfAI is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
