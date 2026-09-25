/**
 * Tarjeta de indicador: valor, tendencia neutra, fuente y fecha de corte.
 * @startingPoint section="Datos" subtitle="Indicador por localidad con fuente y corte" viewport="700x420"
 */
export interface IndicatorCardProps {
  /** Tema en versalitas, p. ej. "Movilidad" */
  kicker?: string;
  locality?: string;
  title: string;
  /** Valor ya formateado en es-CO: "1.284", "58", "92,4" */
  value: string;
  unit?: string;
  /** La dirección nunca implica bueno/malo; se describe con palabra + icono */
  trend?: { direction: 'up' | 'down' | 'flat'; label?: string };
  /** Referencia, p. ej. "Bogotá: 62 min" */
  compare?: string;
  source: string;
  /** Fecha de corte del dato, "30 jun 2026" */
  cutoff: string;
  delayed?: boolean;
}
export declare function IndicatorCard(props: IndicatorCardProps): JSX.Element;
