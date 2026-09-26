"""Limpieza sin inventar fechas ni cantidades de contratos."""
import pandas as pd


def limpiar_datos(df):
    if df is None or df.empty:
        return None, 'No hay datos para procesar'
    data = df.copy()
    aliases = {'monto': 'total', 'amount': 'total', 'valor': 'total',
               'tipo': 'internal_type', 'type': 'internal_type', 'categoria': 'internal_type',
               'contratos': 'contracts', 'cantidad': 'contracts', 'count': 'contracts',
               'mes': 'month', 'fecha': 'date', 'year': 'anio'}
    for source, target in aliases.items():
        if source in data and target not in data:
            data[target] = data[source]
    if 'total' not in data:
        return None, 'La fuente no incluye una columna de monto reconocida.'
    data['total'] = pd.to_numeric(data['total'], errors='coerce')
    data = data.loc[data['total'].notna() & (data['total'] > 0) & (data['total'] < float('inf'))].copy()
    if 'internal_type' in data:
        data['internal_type'] = data['internal_type'].astype('string').str.strip()
        data = data.loc[data['internal_type'].notna() & data['internal_type'].ne('')].copy()
    for name, low, high in [('month', 1, 12), ('anio', 1900, 2100)]:
        values = pd.to_numeric(data[name], errors='coerce') if name in data else pd.Series(float('nan'), index=data.index)
        data[name] = values.where(values.between(low, high) & values.mod(1).eq(0)).astype('Int64')
    if 'date' in data:
        # Evita que números sin unidad se interpreten como nanosegundos desde 1970.
        source = data['date'].astype('string').str.strip()
        source = source.where(~source.str.fullmatch(r'\d+(?:\.\d+)?', na=False))
        dates = pd.to_datetime(source, errors='coerce', format='mixed', utc=True)
        valid = dates.dt.year.between(1900, 2100)
        data['date'] = dates.where(valid)
        # Una fecha completa observada tiene prioridad sobre mes/año inconsistentes.
        data['month'] = data['date'].dt.month.astype('Int64').combine_first(data['month'])
        data['anio'] = data['date'].dt.year.astype('Int64').combine_first(data['anio'])
    if 'contracts' not in data:
        data['contracts'] = float('nan')
    else:
        values = pd.to_numeric(data['contracts'], errors='coerce')
        data['contracts'] = values.where(values.ge(0) & values.lt(float('inf')) & values.mod(1).eq(0))
    if data.empty:
        return None, 'No quedan datos válidos'
    return data, None


def serie_mensual(data):
    """Una fila por mes calendario observado; no completa huecos con ceros."""
    temporal = data.dropna(subset=['anio', 'month', 'total']).copy()
    if temporal.empty:
        return pd.DataFrame(columns=['ds', 'y'])
    temporal['ds'] = pd.to_datetime(dict(year=temporal['anio'].astype(int),
                                       month=temporal['month'].astype(int), day=1))
    return temporal.groupby('ds', as_index=False)['total'].sum().rename(columns={'total': 'y'}).sort_values('ds')
