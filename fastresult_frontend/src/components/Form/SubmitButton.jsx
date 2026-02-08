import { Loader } from 'lucide-react'
import { useEffect } from 'react'
import toast from 'react-hot-toast'

/**
 * SubmitButton: Button with loading state and automatic error toasts
 * Triggers error toast on form submission errors
 */
export default function SubmitButton({
  isLoading = false,
  isError = false,
  errorMessage,
  successMessage,
  onSuccess,
  className = '',
  children = 'Save',
  ...props
}) {
  useEffect(() => {
    if (isError && errorMessage) {
      toast.error(errorMessage)
    }
  }, [isError, errorMessage])

  useEffect(() => {
    if (successMessage) {
      toast.success(successMessage)
      if (onSuccess) {
        setTimeout(onSuccess, 500)
      }
    }
  }, [successMessage, onSuccess])

  return (
    <button
      disabled={isLoading}
      className={`
        px-4 py-2 bg-blue-600 text-white rounded-lg font-medium
        hover:bg-blue-700 transition-colors
        disabled:bg-gray-400 disabled:cursor-not-allowed
        flex items-center justify-center gap-2
        ${className}
      `}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader size={18} className="animate-spin" />
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  )
}
