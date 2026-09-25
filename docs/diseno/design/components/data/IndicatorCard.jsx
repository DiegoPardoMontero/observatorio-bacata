import React from 'react';
const ICONS = {"up":"<polyline points=\"22 7 13.5 15.5 8.5 10.5 2 17\"/><polyline points=\"16 7 22 7 22 13\"/>","down":"<polyline points=\"22 17 13.5 8.5 8.5 13.5 2 7\"/><polyline points=\"16 17 22 17 22 11\"/>","flat":"<path d=\"M5 12h14\"/>","clock":"<circle cx=\"12\" cy=\"12\" r=\"10\"/><polyline points=\"12 6 12 12 16 14\"/>","info":"<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 16v-4\"/><path d=\"M12 8h.01\"/>","pin":"<path d=\"M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0\"/><circle cx=\"12\" cy=\"10\" r=\"3\"/>","chev":"<path d=\"m6 9 6 6 6-6\"/>"};
function Icon({ name }) {
  return <svg className="ico" viewBox="0 0 24 24" aria-hidden="true" dangerouslySetInnerHTML={{ __html: ICONS[name] }} />;
}
const WORD = { up: 'Sube', down: 'Baja', flat: 'Sin cambio' };

export function IndicatorCard({ kicker, locality, title, value, unit, trend, compare, source, cutoff, delayed = false }) {
  return (
    <article className="ind">
      <header className="ind-head">
        {kicker && <span className="ind-kicker">{kicker}</span>}
        {locality && <span className="ind-loc">{locality}</span>}
      </header>
      <h3 className="ind-title">{title}</h3>
      {delayed && <span className="ind-flag"><Icon name="clock" />Datos con retraso</span>}
      <div className="ind-value"><span className="ind-num">{value}</span>{unit && <span className="ind-unit">{unit}</span>}</div>
      {trend && <p className="ind-trend"><Icon name={trend.direction} />{WORD[trend.direction]}{trend.label ? ' ' + trend.label : ''}</p>}
      {compare && <p className="ind-compare">{compare}</p>}
      <footer className="ind-meta"><span>Fuente: <b>{source}</b></span><span>Corte: <span className="tnum">{cutoff}</span></span></footer>
    </article>
  );
}
