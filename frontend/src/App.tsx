import React, { useEffect, useMemo, useState } from 'react';

interface TableItem {
  id: number;
  name: string;
  status: string;
  max_players: number;
  spectator_capacity: number;
  start_time: string | null;
  available_seats?: number;
}

function App() {
  const [tables, setTables] = useState<TableItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [reservationMessage, setReservationMessage] = useState<string>('');
  const [selectedTableId, setSelectedTableId] = useState<number | null>(null);
  const [voiceStatus, setVoiceStatus] = useState<{ enabled: boolean; status: string; message: string } | null>(null);

  const loadTables = async () => {
    try {
      const res = await fetch('/api/v1/tables');
      const data = await res.json();
      setTables(data.items ?? []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadVoiceStatus = async () => {
    try {
      const res = await fetch('/api/v1/livekit/status');
      const data = await res.json();
      setVoiceStatus(data);
    } catch (error) {
      setVoiceStatus({ enabled: false, status: 'error', message: 'وضعیت صدا قابل‌دریافت نیست' });
    }
  };

  useEffect(() => {
    loadTables();
    loadVoiceStatus();
  }, []);

  const reserveTable = async (table: TableItem) => {
    setSelectedTableId(table.id);
    try {
      const res = await fetch(`/api/v1/tables/${table.id}/reserve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, seat_index: 1 }),
      });
      const body = await res.json();
      if (!res.ok) {
        setReservationMessage(body.detail || 'رزرو ناموفق بود');
        return;
      }
      setReservationMessage(`${table.name}: ${body.message}`);
      await loadTables();
    } catch (error) {
      setReservationMessage('خطا در رزرو، دوباره تلاش کنید');
    }
  };

  const waitingTables = useMemo(() => tables.filter((t) => t.status === 'waiting').length, [tables]);
  const playingTables = useMemo(() => tables.filter((t) => t.status === 'playing').length, [tables]);

  return (
    <div className="min-h-screen bg-[#070b16] text-white" dir="rtl">
      <div className="mx-auto max-w-5xl px-4 py-6">
        <header className="mb-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">ROOM 0</p>
          <h1 className="mt-2 text-3xl font-bold">اتاق صفر</h1>
          <p className="mt-2 text-slate-300">رزرو میز، صدا و وضعیت بازی</p>
        </header>

        <main className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">کل میزها</div>
            <div className="mt-3 text-3xl font-bold text-cyan-300">{tables.length}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">در انتظار</div>
            <div className="mt-3 text-3xl font-bold text-emerald-300">{waitingTables}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="text-sm text-slate-400">در حال بازی</div>
            <div className="mt-3 text-3xl font-bold text-yellow-300">{playingTables}</div>
          </div>
        </main>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold">وضعیت صدای زنده</h2>
          </div>
          {voiceStatus ? (
            <div className={`rounded-xl border px-4 py-3 text-sm ${voiceStatus.enabled ? 'border-emerald-500 bg-emerald-500/10 text-emerald-200' : 'border-yellow-500 bg-yellow-500/10 text-yellow-200'}`}>
              {voiceStatus.message}
              <div className="mt-2 text-xs opacity-80">وضعیت: {voiceStatus.status}</div>
            </div>
          ) : null}
        </section>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold">فهرست میزها</h2>
            <button className="rounded-xl border border-cyan-500 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-300">
              ساخت میز جدید
            </button>
          </div>

          {reservationMessage ? (
            <div className="mb-4 rounded-xl border border-cyan-700 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-200">
              {reservationMessage}
            </div>
          ) : null}

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
                      ظرفیت: {table.max_players} بازیکن • تماشاچی: {table.spectator_capacity} • صندلی‌های خالی: {table.available_seats ?? table.max_players}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-medium ${table.status === 'waiting' ? 'text-emerald-400' : table.status === 'playing' ? 'text-cyan-400' : 'text-slate-300'}`}>
                      {table.status}
                    </span>
                    <button
                      onClick={() => reserveTable(table)}
                      disabled={selectedTableId === table.id}
                      className="rounded-xl bg-cyan-600 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {selectedTableId === table.id ? 'در حال رزرو...' : 'رزرو'}
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
