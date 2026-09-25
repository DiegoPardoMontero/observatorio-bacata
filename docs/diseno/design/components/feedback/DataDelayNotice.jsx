import React from 'react';
const ICONS = {"up":"<polyline points=\"22 7 13.5 15.5 8.5 10.5 2 17\"/><polyline points=\"16 7 22 7 22 13\"/>","down":"<polyline points=\"22 17 13.5 8.5 8.5 13.5 2 7\"/><polyline points=\"16 17 22 17 22 11\"/>","flat":"<path d=\"M5 12h14\"/>","clock":"<circle cx=\"12\" cy=\"12\" r=\"10\"/><polyline points=\"12 6 12 12 16 14\"/>","info":"<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 16v-4\"/><path d=\"M12 8h.01\"/>","pin":"<path d=\"M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0\"/><circle cx=\"12\" cy=\"10\" r=\"3\"/>","chev":"<path d=\"m6 9 6 6 6-6\"/>"};
function Icon({ name }) {
  return <svg className="ico" viewBox="0 0 24 24" aria-hidden="true" dangerouslySetInnerHTML={{ __html: ICONS[name] }} />;
}
export function DataDelayNotice({ tone = 'delay', title, children, linkLabel, href }) {
  return (
    <aside className="notice" data-tone={tone} role="status">
      <Icon name={tone === 'info' ? 'info' : 'clock'} />
      <div>
        <p className="notice-title">{title || (tone === 'info' ? 'Sobre estos datos' : 'Estos datos llegan con retraso')}</p>
        <p className="notice-body">{children}</p>
        {linkLabel && <a className="notice-link" href={href}>{linkLabel}</a>}
      </div>
    </aside>
  );
}
