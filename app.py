import logging

from aiogram import Bot, Dispatcher, executor, types
from aiohttp import ClientSession

from config import API_TOKEN
from keyboards import book_keyboard, recent_books_list

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(text="Assalomu alaykum @dbooksdebot botimizga xush kelibsiz. Bu bot sizga dbooks.org saytidan kitob qidirish va kitobni yuklab olishga yordam beradi. Kitobni qidirish uchun nomini kiriting:")



@dp.message_handler(content_types="text")
async def search_book(message: types.Message):
    async with ClientSession() as session:
        try:
            response = await session.get(url='https://www.dbooks.org/api/search/' + message.text)
            data = await response.json()
            status = data['status']
            if status == "ok":
                books = data["books"][:20]
                ans_title = f"Natijalar: {len(books)}"
                ans_content = [f"<b>{i + 1}.</b> " + books[i]['title'] + "   -   " + f"<i>{books[i]['authors']}</i>"
                               for i in range(len(books))]

                ans = ans_title + "\n\n" + "\n\n".join(ans_content)
                await message.answer(text=ans, reply_markup=recent_books_list(books_data=books))
            else:
                await message.answer(text="Kitob topilmadi. 😭")
        except Exception as e:
            logging.info(e)


@dp.callback_query_handler(lambda call: call.data.startswith("id_"))
async def choosing_interests(query: types.CallbackQuery):
    await query.message.delete()
    data = query.data
    book_id = data.split("_")[1]
    async with ClientSession() as session:
        try:
            response = await session.get(url='https://www.dbooks.org/api/book/' + book_id)
            data = await response.json()
            status = data['status']
            if status == "ok":
                book_title = data['title']
                book_description = data['description']
                book_authors = data['authors']
                book_publisher = data['publisher']
                book_pages = data['pages']
                book_year = data['year']
                book_image = data['image']
                book_url = data['url']
                book_download = data['download']

                content = f"<b>Sarlavha:</b> {book_title}\n\n" \
                          f"<b>Tavsif:</b> {book_description}\n\n" \
                          f"<b>Muallif:</b> <i>{book_authors}</i>\n\n" \
                          f"<b>Nashriyotchi:</b> {book_publisher}\n" \
                          f"<b>Sahifalar:</b> {book_pages}\n" \
                          f"<b>Yili:</b> {book_year}\n" \

                await query.message.answer_photo(
                    photo=book_image,
                    caption=content,
                    reply_markup=book_keyboard(url=book_url, download=book_download)
                )

        except Exception as e:
            logging.info(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
