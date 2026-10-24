import React, { useEffect, useState } from 'react';

interface TableItem {
  id: number;
  name: string;
  status: string;
  max_players: number;
  spectator_capacity: number;
  start_time: string | null;
}

function App() {
  const [tables, setTables] = useState<TableItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/tables')
      .then((res) => res.json())
      .then((data) => {
        setTables(data.items || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const statusColors: Record<string, string> = {
    waiting: 'text-emerald-400',
    reserved: 'text-yellow-400',
    playing: 'text-cyan-400',
    locked: 'text-red-400',
    finished: 'text-slate-400',
  };

  return (
    <div className="min-h-screen bg-[#070b16] text-white" dir="rtl">
      <div className="mx-auto max-w-5xl px-4 py-6">
        <header className="mb-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">ROOM 0</p>
          <h1 className="mt-2 text-3xl font-bold">اتاق صفر</h1>
          <p className="mt-2 text-slate-300">داشبورد میزها و وضعیت بازی</p>
        </header>

        <main className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">کل میزها</div>
            <div className="mt-3 text-3xl font-bold text-cyan-300">{tables.length}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">در انتظار</div>
            <div className="mt-3 text-3xl font-bold text-emerald-300">
              {tables.filter((t) => t.status === 'waiting').length}
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">در حال بازی</div>
            <div className="mt-3 text-3xl font-bold text-yellow-300">
              {tables.filter((t) => t.status === 'playing').length}
            </div>
          </div>
        </main>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">فهرست میزها</h2>
            <button className="rounded-xl border border-cyan-500 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-300">
              رزرو جدید
            </button>
          </div>

          {loading ? (
            <div className="text-slate-400">در حال بارگذاری...</div>
          ) : tables.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-700 p-6 text-center text-slate-400">
              هیچ میز فعلی وجود ندارد.
            </div>
          ) : (
            <div className="space-y-3">
              {tables.map((table) => (
                <div key={table.id} className="flex flex-col gap-3 rounded-xl border border-slate-700 bg-slate-800 p-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="text-lg font-semibold">{table.name}</div>
                    <div className="mt-1 text-sm text-slate-400">
                      ظرفیت: {table.max_players} بازیکن • تماشاچی: {table.spectator_capacity}
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className={`text-sm font-medium ${statusColors[table.status] || 'text-slate-300'}`}>
                      {table.status}
                    </span>
                    <button className="rounded-xl bg-cyan-600 px-3 py-2 text-sm font-medium text-white">
                      رزرو
                    </button>
                    <button className="rounded-xl border border-slate-600 px-3 py-2 text-sm text-slate-200">
                      انتظار
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;
