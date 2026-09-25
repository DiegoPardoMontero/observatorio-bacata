/**
 * Aviso sereno de que la fuente no ha publicado un corte nuevo. Nunca rojo.
 * @startingPoint section="Avisos" subtitle="Aviso de datos retrasados" viewport="700x280"
 */
export interface DataDelayNoticeProps {
  /** 'delay' (oro) cuando el corte esperado no llegó; 'info' (cerro) para notas metodológicas */
  tone?: 'delay' | 'info';
  title?: string;
  children: React.ReactNode;
  linkLabel?: string;
  href?: string;
}
export declare function DataDelayNotice(props: DataDelayNoticeProps): JSX.Element;
