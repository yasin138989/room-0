# ROOM 0 Architecture

## پلتفرم

- Frontend: React + TypeScript + Vite + Tailwind
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL
- Cache: Redis
- Optional voice: LiveKit

## اصول

- وضعیت معتبر تنها در سرور است.
- نقش‌ها فقط برای کاربر مربوطه و سرور قابل مشاهده‌اند.
- احراز هویت بر اساس `Telegram initData` انجام می‌شود.
- API عمومی از داده‌های خصوصی نقش‌ها چشم‌پوشی می‌کند.
- همه عملیات مهم، تراکنش‌دار و قابل ثبت هستند.

## قرارداد رویدادها

- `table.created`
- `table.updated`
- `seat.reserved`
- `seat.released`
- `game.started`
- `vote.submitted`
- `game.finished`
- `connection.restored`
