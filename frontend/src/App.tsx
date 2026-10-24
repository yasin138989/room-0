function App() {
  return (
    <div className="min-h-screen bg-[#070b16] text-white">
      <div className="mx-auto max-w-4xl px-4 py-10">
        <header className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-glow">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">ROOM 0</p>
          <h1 className="mt-2 text-3xl font-bold text-white">اتاق صفر</h1>
          <p className="mt-3 text-slate-300">بازی اجتماعی و استنتاجی در Telegram Mini App</p>
        </header>

        <main className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">وضعیت میزها</div>
            <div className="mt-3 text-3xl font-bold text-cyan-300">12</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">بازیکنان آنلاین</div>
            <div className="mt-3 text-3xl font-bold text-emerald-300">48</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">تماشاچی‌ها</div>
            <div className="mt-3 text-3xl font-bold text-yellow-300">7</div>
          </div>
        </main>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <h2 className="text-xl font-semibold text-white">میزهای موجود</h2>
          <ul className="mt-4 space-y-3">
            <li className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 p-3">
              <span>میز 01</span>
              <span className="text-emerald-400">در انتظار</span>
            </li>
            <li className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 p-3">
              <span>میز 02</span>
              <span className="text-yellow-400">در حال رزرو</span>
            </li>
            <li className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 p-3">
              <span>میز 03</span>
              <span className="text-cyan-400">در حال بازی</span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}

export default App;
