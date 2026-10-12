import React, { useRef, useState } from 'react'
import { CornerGrid } from '../common/CornerGrid'
import { Camera, Upload, Loader2, Sparkles } from 'lucide-react'
import { buildApiUrl, getAuthHeaders } from '../../utils/apiConfig'

interface AddressImageUploadProps {
  onAddressesExtracted: (data: { sender: any; customer: any; raw_text: string }) => void
  onNotify: (msg: string) => void
}

export const AddressImageUpload: React.FC<AddressImageUploadProps> = ({
  onAddressesExtracted,
  onNotify,
}) => {
  const [isUploading, setIsUploading] = useState<boolean>(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (file: File) => {
    if (!file) return

    setIsUploading(true)
    onNotify('Running OCR on address photograph...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(buildApiUrl('/api/v1/ocr/extract-address'), {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized (401): Missing or invalid API key. Open settings in the top bar to configure.')
        }
        let detail = response.statusText
        try {
          const errData = await response.json()
          if (errData.detail) detail = errData.detail
        } catch {
          // ignore
        }
        throw new Error(`OCR failed: ${detail}`)
      }

      const data = await response.json()
      if (data.success) {
        onAddressesExtracted({
          sender: data.sender,
          customer: data.customer,
          raw_text: data.raw_text,
        })
        onNotify('Extracted addresses from photo. Please review!')
      } else {
        throw new Error('Could not parse addresses')
      }
    } catch (err: any) {
      onNotify(`OCR Error: ${err.message || 'Failed to process image'}`)
    } finally {
      setIsUploading(false)
    }
  }

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFileUpload(file)
  }

  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm cursor-default">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3 mb-4">
        <div className="flex items-center gap-2">
          <CornerGrid />
          <span className="section-label">SINGLE-PHOTO ADDRESS OCR</span>
        </div>
        <div className="flex items-center gap-1 font-mono-tech text-[10px] text-[var(--text-secondary)]">
          <Sparkles className="h-3 w-3 text-[var(--accent-red)]" />
          <span>AUTO DETECTS SENDER & CUSTOMER</span>
        </div>
      </div>

      {/* Hidden File Inputs */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={onFileChange}
        accept="image/*"
        className="hidden"
      />
      <input
        type="file"
        ref={cameraInputRef}
        onChange={onFileChange}
        accept="image/*"
        capture="environment"
        className="hidden"
      />

      {/* Upload Dropzone Container */}
      <div className="rounded-lg border-2 border-dashed border-[var(--border-color)] hover:border-[var(--accent-red)] bg-[var(--bg-card)] p-6 text-center transition-all duration-200 cursor-pointer shadow-sm">
        {isUploading ? (
          <div className="py-4 space-y-3">
            <Loader2 className="h-8 w-8 text-[var(--accent-red)] animate-spin mx-auto" />
            <div className="font-mono-tech text-xs tracking-wider text-[var(--text-primary)] uppercase font-bold">
              Processing Image with Address OCR...
            </div>
            <p className="font-mono-tech text-[10px] text-[var(--text-secondary)]">
              Preprocessing contrast and identifying TO & FROM blocks
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center gap-3">
              <button
                type="button"
                onClick={() => cameraInputRef.current?.click()}
                className="btn-primary py-2.5 px-4 text-xs flex items-center gap-2"
                title="Snap photo with camera"
              >
                <Camera className="h-4 w-4" />
                <span>TAKE PHOTO (CAMERA)</span>
              </button>

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn-secondary py-2.5 px-4 text-xs flex items-center gap-2"
                title="Select image from laptop"
              >
                <Upload className="h-4 w-4 text-[var(--accent-red)]" />
                <span>UPLOAD IMAGE FILE</span>
              </button>
            </div>

            <p className="font-mono-tech text-[10.5px] text-[var(--text-muted)]">
              Upload ONE photograph containing both sender & customer addresses.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
