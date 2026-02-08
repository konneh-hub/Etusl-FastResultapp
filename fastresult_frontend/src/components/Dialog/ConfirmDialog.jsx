import { Trash2 } from 'lucide-react'

/**
 * ConfirmDialog: Modal for confirming destructive actions (delete, etc)
 */
export default function ConfirmDialog({
  isOpen,
  onConfirm,
  onCancel,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Delete',
  cancelText = 'Cancel',
  isLoading = false,
  isDangerous = true
}) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm">
        <div className="flex items-center gap-3 mb-4">
          {isDangerous && (
            <div className="p-2 bg-red-100 rounded-full">
              <Trash2 size={20} className="text-red-600" />
            </div>
          )}
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        </div>

        <p className="text-gray-600 mb-6">{message}</p>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium
              hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={`px-4 py-2 text-white rounded-lg font-medium transition-colors
              ${isDangerous
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-red-400'
                : 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400'
              }`}
          >
            {isLoading ? 'Processing...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
