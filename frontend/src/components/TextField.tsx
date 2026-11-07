import { TextInput, type TextInputProps } from '@mantine/core'
import { useState, type ChangeEvent, type FocusEvent } from 'react'

export interface TextFieldProps extends Omit<TextInputProps, 'label'> {
  label: string
  /** Validación básica al salir del campo: devuelve el mensaje de error o null si es válido. */
  validate?: (value: string) => string | null
}

export function TextField({ label, validate, error, onBlur, onChange, size = 'lg', ...props }: TextFieldProps) {
  const [blurError, setBlurError] = useState<string | null>(null)

  const handleBlur = (event: FocusEvent<HTMLInputElement>) => {
    if (validate) setBlurError(validate(event.currentTarget.value))
    onBlur?.(event)
  }

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (blurError) setBlurError(null)
    onChange?.(event)
  }

  return (
    <TextInput
      label={label}
      size={size}
      error={error ?? blurError}
      onBlur={handleBlur}
      onChange={handleChange}
      {...props}
    />
  )
}
