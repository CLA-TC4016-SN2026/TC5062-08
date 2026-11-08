/** Genera una clave `Idempotency-Key` por intención del usuario. Se reutiliza en los reintentos de la misma acción. */
export const newIdempotencyKey = (): string => crypto.randomUUID()
