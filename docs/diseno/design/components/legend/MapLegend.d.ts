/**
 * Leyenda de mapa coroplético con escala secuencial o divergente.
 * @startingPoint section="Datos" subtitle="Leyenda secuencial o divergente con 'sin dato'" viewport="700x300"
 */
export interface MapLegendProps {
  title: string;
  unit?: string;
  type?: 'sequential' | 'diverging';
  /** 3–7 clases. Divergente: número impar */
  steps?: number;
  /** steps + 1 cortes, ya formateados */
  ticks?: string[];
  lowLabel?: string;
  highLabel?: string;
  showNoData?: boolean;
  /** Muestra la clave del contorno oro para la localidad elegida */
  selectedLabel?: string;
}
export declare function MapLegend(props: MapLegendProps): JSX.Element;
