import React from 'react';
const SEQ = [1,2,3,4,5,6,7].map(i => 'var(--data-seq-' + i + ')');
const DIV = ['n3','n2','n1','0','p1','p2','p3'].map(k => 'var(--data-div-' + k + ')');

export function MapLegend({ title, unit, type = 'sequential', steps = 5, ticks = [], lowLabel, highLabel, showNoData = true, selectedLabel }) {
  const pal = type === 'diverging' ? DIV : SEQ;
  const colors = type === 'diverging'
    ? pal.slice((7 - steps) / 2, (7 - steps) / 2 + steps)
    : pal.slice(steps >= 7 ? 0 : 1, (steps >= 7 ? 0 : 1) + steps);
  return (
    <div className="legend" role="group" aria-label={'Leyenda: ' + title}>
      <p className="legend-title">{title}</p>
      {unit && <p className="legend-unit">{unit}</p>}
      <div className="legend-scale">{colors.map((c, i) => <span key={i} style={{ background: c }} />)}</div>
      {ticks.length > 0 && <div className="legend-ticks">{ticks.map((t, i) => <span key={i}>{t}</span>)}</div>}
      {(lowLabel || highLabel) && <div className="legend-ends"><span>{lowLabel}</span><span>{highLabel}</span></div>}
      {(showNoData || selectedLabel) && (
        <div className="legend-extra">
          {showNoData && <span className="legend-key"><span className="legend-swatch is-nodata" />Sin dato</span>}
          {selectedLabel && <span className="legend-key"><span className="legend-swatch is-selected" />{selectedLabel}</span>}
        </div>
      )}
    </div>
  );
}
