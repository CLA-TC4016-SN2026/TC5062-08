import { Alert, Group, Pagination, Skeleton, Stack, Text, Title, VisuallyHidden } from '@mantine/core'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { AppButton } from '../components/AppButton'
import { InfoCard } from '../components/InfoCard'
import { useMiRepositorio } from '../hooks/useMiRepositorio'
import { ApiError, documentoService, getErrorMessage, type Documento } from '../services'

const POR_PAGINA = 5

const TIPO: Record<NonNullable<Documento['tipo']>, string> = {
  laboratorio: 'Laboratorio',
  informe_imagen: 'Informe de imagen',
  receta: 'Receta',
  otro: 'Otro',
}
const ESTADO: Record<Documento['estado'], string> = {
  pendiente_confirmacion: 'Pendiente de confirmación',
  confirmado: 'Confirmado',
}

const formatoFecha = new Intl.DateTimeFormat('es', { day: 'numeric', month: 'long', year: 'numeric' })

// `fechaDocumento` llega como YYYY-MM-DD: con `new Date(texto)` se interpretaría en UTC y en zonas
// horarias al oeste de Greenwich mostraría el día anterior.
function fechaDelDocumento(iso: string): string {
  const [anio, mes, dia] = iso.split('-').map(Number)
  return formatoFecha.format(new Date(anio, mes - 1, dia))
}

function tamano(bytes: number): string {
  return bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function DocumentoTarjeta({ documento }: { documento: Documento }) {
  return (
    <InfoCard title={documento.nombreArchivo}>
      <Text>Tipo: {documento.tipo ? TIPO[documento.tipo] : 'Por confirmar'}</Text>
      <Text>
        Fecha del documento: {documento.fechaDocumento ? fechaDelDocumento(documento.fechaDocumento) : 'Por confirmar'}
      </Text>
      <Text fw={600}>Estado: {ESTADO[documento.estado]}</Text>
      <Text c="dimmed" size="sm">
        Subido el {formatoFecha.format(new Date(documento.subidoEn))} · {documento.formato.toUpperCase()} · {tamano(documento.tamanoBytes)}
      </Text>
    </InfoCard>
  )
}

export function DocumentosPage() {
  const [pagina, setPagina] = useState(1)
  const repositorio = useMiRepositorio()
  const repositorioId = repositorio.data?.id
  // Se recuerda el total para no perder la paginación si una página falla y no hay datos que la calculen.
  const [totalConocido, setTotalConocido] = useState<number | null>(null)
  const documentos = useQuery({
    queryKey: ['documentos', repositorioId, pagina],
    queryFn: async () => {
      const resultado = await documentoService.listar(repositorioId!, { pagina, tamanoPagina: POR_PAGINA })
      setTotalConocido(resultado.total)
      return resultado
    },
    enabled: !!repositorioId,
    placeholderData: keepPreviousData,
    retry: false,
  })

  const error = repositorio.error ?? documentos.error
  const cargando = !error && (repositorio.isPending || documentos.isPending)
  const reintentar = () => (repositorio.isError ? repositorio.refetch() : documentos.refetch())
  const total = documentos.data?.total ?? totalConocido
  const totalPaginas = total ? Math.ceil(total / POR_PAGINA) : 0

  return (
    <Stack>
      <Title order={1} size="h2">Mis documentos</Title>

      {cargando && (
        <Stack role="status" aria-busy="true">
          <VisuallyHidden>Cargando documentos…</VisuallyHidden>
          {Array.from({ length: POR_PAGINA }, (_, i) => (
            <Skeleton key={i} height={132} radius="md" />
          ))}
        </Stack>
      )}

      {error &&
        (error instanceof ApiError && error.status === 404 ? (
          <Text>Todavía no tienes un repositorio.</Text>
        ) : (
          <Stack align="flex-start">
            <Alert
              color="red"
              title={documentos.data ? 'No se pudo actualizar la lista de documentos' : 'No se pudieron cargar tus documentos'}
              w="100%"
            >
              {documentos.data && 'Estás viendo la última versión guardada. '}
              {getErrorMessage(error)}
            </Alert>
            {/* Fuera de la alerta: el botón de contorno azul no alcanza 4.5:1 sobre el fondo rojo tintado. */}
            <AppButton variant="secondary" onClick={reintentar} loading={repositorio.isFetching || documentos.isFetching}>
              Reintentar
            </AppButton>
          </Stack>
        ))}

      {documentos.data &&
        (documentos.data.total === 0 ? (
          <Text>Aún no has subido documentos.</Text>
        ) : (
          <>
            <Text c="dimmed" role="status">
              {documentos.data.total} {documentos.data.total === 1 ? 'documento' : 'documentos'}
            </Text>
            <Stack component="ul" p={0} m={0} style={{ listStyle: 'none', opacity: documentos.isPlaceholderData ? 0.6 : 1 }} aria-busy={documentos.isPlaceholderData}>
              {documentos.data.items.map((documento) => (
                <li key={documento.id}>
                  <DocumentoTarjeta documento={documento} />
                </li>
              ))}
            </Stack>
          </>
        ))}

      {totalPaginas > 1 && (
        <Group justify="center">
          <Pagination
            total={totalPaginas}
            value={pagina}
            onChange={setPagina}
            disabled={documentos.isPlaceholderData}
            size="lg"
            getControlProps={(control) => ({
              'aria-label': { first: 'Primera página', previous: 'Página anterior', next: 'Página siguiente', last: 'Última página' }[control],
            })}
            getItemProps={(page) => ({ 'aria-label': `Página ${page}` })}
          />
        </Group>
      )}
    </Stack>
  )
}
