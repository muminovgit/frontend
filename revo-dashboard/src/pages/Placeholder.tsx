export function Placeholder({ title }: { title: string }) {
  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>{title}</h1>
          <p className="muted">Bu bo'lim tez orada qo'shiladi.</p>
        </div>
      </div>
    </section>
  );
}
