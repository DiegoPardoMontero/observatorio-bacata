/**
 * Selector nativo de las 20 localidades — abre el selector del sistema en el celular.
 * @startingPoint section="Formularios" subtitle="Selector de localidad táctil" viewport="700x220"
 */
export interface LocalitySelectorProps {
  /** Nombre de la localidad, p. ej. "Kennedy" */
  value: string;
  onChange?: (value: string) => void;
  label?: string;
  hint?: string;
  id?: string;
}
export declare function LocalitySelector(props: LocalitySelectorProps): JSX.Element;
export declare const LOCALIDADES: string[];
