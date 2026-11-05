// Shared scientific chart typography and spacing. Axis overrides retain the
// spacing rules even when a caller supplies its own scale, range or title.
const sans = 'Inter, Arial, sans-serif';
const mono = 'IBM Plex Mono, monospace';
function axis(label, options = {}) {
  const title = typeof options.title === 'string' ? {text: options.title} : options.title || {};
  return {
    automargin: true,
    zeroline: true, zerolinecolor: '#b5c0d2', zerolinewidth: 1,
    gridcolor: '#e7edf5', gridwidth: 1,
    showline: true, linecolor: '#cbd5e3', linewidth: 1,
    ticks: 'outside', ticklen: 5, tickcolor: '#cbd5e3',
    nticks: 6, exponentformat: 'power', showexponent: 'all',
    ...options,
    tickfont: {family: mono, size: 12, color: '#475871', ...options.tickfont},
    title: {text: label, standoff: 20, ...title,
      font: {family: sans, size: 13, color: '#34445e', ...title.font}},
  };
}

export function chartLayout(extra = {}) {
  return {
    paper_bgcolor: 'transparent', plot_bgcolor: '#ffffff',
    colorway: ['#5746bb', '#97612b', '#496f96', '#a54662'],
    hovermode: 'closest',
    ...extra,
    margin: {l: 96, r: 28, t: 92, b: 76, ...extra.margin},
    font: {family: sans, color: '#475871', size: 13, ...extra.font},
    xaxis: axis('x', extra.xaxis),
    yaxis: axis('y', extra.yaxis),
    legend: {
      orientation: 'h', x: 0, xanchor: 'left', y: 1.12, yanchor: 'bottom',
      bgcolor: 'rgba(255,255,255,0.94)', borderwidth: 0,
      itemsizing: 'constant', tracegroupgap: 8,
      ...extra.legend,
      font: {family: sans, size: 12, color: '#34445e', ...extra.legend?.font},
    },
    hoverlabel: {bgcolor: '#172c43', bordercolor: '#172c43',
      ...extra.hoverlabel, font: {family: sans, size: 13, color: '#ffffff', ...extra.hoverlabel?.font}},
  };
}
