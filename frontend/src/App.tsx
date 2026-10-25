import { useState, useEffect, useCallback } from 'react'
import { Header } from './components/layout/Header'
import { SegmentedNav, type NavTab } from './components/layout/SegmentedNav'
import { ToastBanner } from './components/common/ToastBanner'
import { VoiceItemInput } from './components/items/VoiceItemInput'
import { ManualItemTable } from './components/items/ManualItemTable'
import { AddressDetailsCard } from './components/documents/AddressDetailsCard'
import { DocumentDownloadCard } from './components/documents/DocumentDownloadCard'
import { BookingAwbCard } from './components/booking/BookingAwbCard'
import { DocumentHistoryView } from './components/history/DocumentHistoryView'
import { AddressImageUpload } from './components/address/AddressImageUpload'
import { AddressReviewModal } from './components/address/AddressReviewModal'
import type { ItemLine } from './types/item'
import type { AddressInfo, DocumentGenerationPayload } from './types/document'
import { buildApiUrl, getAuthHeaders } from './utils/apiConfig'
import { getIndiaDate, getCountrySlug } from './utils/dateUtils'
import { ArrowLeft } from 'lucide-react'

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('invoice')
  const [toastMessage, setToastMessage] = useState<string>('')
  const [showToast, setShowToast] = useState<boolean>(false)

  // Sub-view mode for each tab ('list' shows saved files first; 'form' shows creation form after tapping + NEW)
  const [invoiceViewMode, setInvoiceViewMode] = useState<'list' | 'form'>('list')
  const [addressViewMode, setAddressViewMode] = useState<'list' | 'form'>('list')
  const [bookingViewMode, setBookingViewMode] = useState<'list' | 'form'>('list')

  // Dark / Light Mode Theme State
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('smartinvoice_theme') as 'dark' | 'light') || 'dark'
  })

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light')
    } else {
      document.documentElement.classList.remove('light')
    }
  }, [theme])

  const handleToggleTheme = () => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark'
      localStorage.setItem('smartinvoice_theme', next)
      return next
    })
  }

  // OCR Review State
  const [pendingOcrData, setPendingOcrData] = useState<{
    sender: AddressInfo
    customer: AddressInfo
    raw_text: string
  } | null>(null)

  // Document metadata
  const [docNumber, setDocNumber] = useState<string>('INV-2026-0001')
  const [addressNumber, setAddressNumber] = useState<string>('ADD-USA-0001')
  const [awbNumber, setAwbNumber] = useState<string>('AWB-USA-0001')
  const [docDate, setDocDate] = useState<string>(getIndiaDate())
  const [includeInvoice, setIncludeInvoice] = useState<boolean>(true)
  const [includeAddressLabel, setIncludeAddressLabel] = useState<boolean>(false)
  const [addressFormat, setAddressFormat] = useState<'pdf' | 'docx'>('pdf')
  const [invoiceFormat, setInvoiceFormat] = useState<'pdf' | 'xlsx'>('pdf')
  const [weight, setWeight] = useState<string>('')
  const [invoiceAwbNumber, setInvoiceAwbNumber] = useState<string>('')
  const [invoiceContentsDescription, setInvoiceContentsDescription] = useState<string>('')

  // Address Details State (Clean, empty by default for new parcel input or photo OCR)
  const [sender, setSender] = useState<AddressInfo>({
    name: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    postal_code: '',
    phone: '',
    gstin: '',
  })

  const [customer, setCustomer] = useState<AddressInfo>({
    name: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    postal_code: '',
    phone: '',
  })

  // Items State (Empty by default)
  const [items, setItems] = useState<ItemLine[]>([])
  const [customTotal, setCustomTotal] = useState<string>('0.00')
  const [isManualTotalEdited, setIsManualTotalEdited] = useState<boolean>(false)

  // Automatically fetch next sequential document number from backend
  const fetchNextDocNumber = useCallback(async (tab: NavTab = activeTab, targetCountry?: string) => {
    if (tab === 'invoice') {
      try {
        const res = await fetch(buildApiUrl(`/api/v1/documents/next-number?doc_type=invoice`), {
          headers: getAuthHeaders(),
        })
        if (res.ok) {
          const data = await res.json()
          if (data.next_number) {
            setDocNumber(data.next_number)
          }
        }
      } catch {
        // Keep existing default
      }
    } else if (tab === 'address') {
      const countryStr = targetCountry || customer.state || customer.city || 'USA'
      const slug = getCountrySlug(countryStr)
      try {
        const res = await fetch(buildApiUrl(`/api/v1/documents/next-number?doc_type=address&country=${encodeURIComponent(slug)}`), {
          headers: getAuthHeaders(),
        })
        if (res.ok) {
          const data = await res.json()
          if (data.next_number) {
            setAddressNumber(data.next_number)
          }
        }
      } catch {
        // Keep existing default
      }
    } else if (tab === 'booking') {
      const countryStr = targetCountry || customer.state || customer.city || 'USA'
      const slug = getCountrySlug(countryStr)
      try {
        const res = await fetch(buildApiUrl(`/api/v1/documents/next-number?doc_type=booking&country=${encodeURIComponent(slug)}`), {
          headers: getAuthHeaders(),
        })
        if (res.ok) {
          const data = await res.json()
          if (data.next_number) {
            setAwbNumber(data.next_number)
          }
        }
      } catch {
        // Keep existing default
      }
    }
  }, [activeTab, customer.city, customer.state])

  // Switch tabs smoothly
  const handleSelectTab = (tab: NavTab) => {
    setActiveTab(tab)
    fetchNextDocNumber(tab)
  }

  useEffect(() => {
    fetchNextDocNumber('invoice')
    fetchNextDocNumber('address')
    fetchNextDocNumber('booking')
  }, [fetchNextDocNumber])

  // Auto-calculate suggested total as sum of (quantity * unit price)
  useEffect(() => {
    if (!isManualTotalEdited) {
      let sum = 0
      for (const it of items) {
        const qty = parseFloat(it.count) || 1
        const unitPrice = parseFloat(it.price.replace(/,/g, '')) || 0
        sum += qty * unitPrice
      }
      const formatted = sum > 0 ? sum.toFixed(2) : '0.00'
      setCustomTotal((prev) => (prev !== formatted ? formatted : prev))
    }
  }, [items, isManualTotalEdited])

  const triggerToast = (msg: string) => {
    setToastMessage(msg)
    setShowToast(true)
    setTimeout(() => setShowToast(false), 2600)
  }

  // OCR Callbacks
  const handleAddressesExtracted = (data: { sender: any; customer: any; raw_text: string }) => {
    setPendingOcrData({
      sender: {
        name: data.sender.name || '',
        address_line_1: data.sender.address_line_1 || '',
        address_line_2: data.sender.address_line_2 || '',
        city: data.sender.city || '',
        state: data.sender.state || '',
        postal_code: data.sender.postal_code || '',
        phone: data.sender.phone || '',
        gstin: data.sender.gstin || '',
      },
      customer: {
        name: data.customer.name || '',
        address_line_1: data.customer.address_line_1 || '',
        address_line_2: data.customer.address_line_2 || '',
        city: data.customer.city || '',
        state: data.customer.state || '',
        postal_code: data.customer.postal_code || '',
        phone: data.customer.phone || '',
        gstin: data.customer.gstin || '',
      },
      raw_text: data.raw_text,
    })
  }

  const handleConfirmOcr = (reviewedSender: AddressInfo, reviewedCustomer: AddressInfo) => {
    setSender(reviewedSender)
    setCustomer(reviewedCustomer)
    setPendingOcrData(null)
    triggerToast('Applied confirmed addresses to invoice')
  }

  // Item management callbacks
  const handleAddItemFromVoice = (newItem: Omit<ItemLine, 'id'>) => {
    const id = Date.now().toString()
    setItems((prev) => [...prev, { id, ...newItem }])
  }

  const handleAddBlankRow = () => {
    const id = Date.now().toString()
    setItems((prev) => [...prev, { id, name: '', count: '1', price: '0' }])
    triggerToast('Added new item row')
  }

  const handleUpdateItem = (id: string, field: keyof ItemLine, value: string) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    )
  }

  const handleRemoveItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id))
    triggerToast('Item removed')
  }

  const handleUpdateCustomTotal = (val: string) => {
    setIsManualTotalEdited(true)
    setCustomTotal(val)
  }

  const handleResetAutoTotal = () => {
    setIsManualTotalEdited(false)
    let sum = 0
    for (const it of items) {
      const qty = parseFloat(it.count) || 1
      const unitPrice = parseFloat(it.price.replace(/,/g, '')) || 0
      sum += qty * unitPrice
    }
    setCustomTotal(sum > 0 ? sum.toFixed(2) : '0.00')
    triggerToast('Reset to sum of items')
  }

  const handleUpdateSender = (field: keyof AddressInfo, val: string) => {
    setSender((prev) => ({ ...prev, [field]: val }))
  }

  const handleUpdateCustomer = (field: keyof AddressInfo, val: string) => {
    setCustomer((prev) => {
      const updated = { ...prev, [field]: val }
      if (field === 'state' || field === 'city') {
        fetchNextDocNumber('address', updated.state || updated.city)
        fetchNextDocNumber('booking', updated.state || updated.city)
      }
      return updated
    })
  }

  const handleNewInvoice = () => {
    setSender({ name: '', address_line_1: '', address_line_2: '', city: '', state: '', postal_code: '', phone: '', gstin: '' })
    setCustomer({ name: '', address_line_1: '', address_line_2: '', city: '', state: '', postal_code: '', phone: '' })
    setItems([])
    setCustomTotal('0.00')
    setIsManualTotalEdited(false)
    setWeight('')
    setInvoiceAwbNumber('')
    setInvoiceContentsDescription('')
    setDocDate(getIndiaDate())
    fetchNextDocNumber('invoice')
    setInvoiceViewMode('form')
  }

  const handleNewAddress = () => {
    setSender({ name: '', address_line_1: '', address_line_2: '', city: '', state: '', postal_code: '', phone: '', gstin: '' })
    setCustomer({ name: '', address_line_1: '', address_line_2: '', city: '', state: '', postal_code: '', phone: '' })
    setDocDate(getIndiaDate())
    fetchNextDocNumber('address')
    setAddressViewMode('form')
  }

  const handleNewBooking = () => {
    setSender({ name: '', address_line_1: '', address_line_2: '', city: '', state: '', postal_code: '', phone: '', gstin: '' })
    setCustomer({ name: '', address_line_1: '', address_line_2: '', city: '', state: '', postal_code: '', phone: '' })
    setDocDate(getIndiaDate())
    setWeight('')
    fetchNextDocNumber('booking')
    setBookingViewMode('form')
  }

  const handleLoadDocumentFromHistory = (doc: any) => {
    const isBooking = doc.doc_type === 'booking' || doc.doc_type === 'awb' || doc.doc_number?.startsWith('AWB-')
    const isAddress = doc.doc_type === 'address' || doc.doc_number?.startsWith('ADD-')

    if (isBooking) {
      if (doc.doc_number) setAwbNumber(doc.doc_number)
      if (doc.date) setDocDate(doc.date)
      if (doc.sender) setSender(doc.sender)
      if (doc.customer) setCustomer(doc.customer)
      if (doc.weight) setWeight(doc.weight)
      setActiveTab('booking')
      setBookingViewMode('form')
      triggerToast(`Loaded Booking #${doc.doc_number}`)
    } else if (isAddress) {
      if (doc.doc_number) setAddressNumber(doc.doc_number)
      if (doc.date) setDocDate(doc.date)
      if (doc.sender) setSender(doc.sender)
      if (doc.customer) setCustomer(doc.customer)
      setActiveTab('address')
      setAddressViewMode('form')
      triggerToast(`Loaded Address #${doc.doc_number}`)
    } else {
      if (doc.doc_number) setDocNumber(doc.doc_number)
      if (doc.date) setDocDate(doc.date)
      if (doc.sender) setSender(doc.sender)
      if (doc.customer) setCustomer(doc.customer)
      if (doc.items && Array.isArray(doc.items)) setItems(doc.items)
      if (doc.total) {
        setCustomTotal(doc.total)
        setIsManualTotalEdited(true)
      }
      if (doc.weight) setWeight(doc.weight)
      if (doc.awb_number) setInvoiceAwbNumber(doc.awb_number)
      if (doc.contents_description) setInvoiceContentsDescription(doc.contents_description)
      setActiveTab('invoice')
      setInvoiceViewMode('form')
      triggerToast(`Loaded Invoice #${doc.doc_number}`)
    }
  }

  const downloadPayload: DocumentGenerationPayload = {
    doc_type: 'invoice',
    doc_number: docNumber,
    date: docDate,
    sender,
    customer,
    items,
    total: customTotal,
    include_invoice: includeInvoice,
    include_address_label: includeAddressLabel,
    address_format: addressFormat,
    invoice_format: invoiceFormat,
    weight,
    awb_number: invoiceAwbNumber,
    contents_description: invoiceContentsDescription,
  }

  const handleUpdateDownloadField = (field: keyof DocumentGenerationPayload, value: any) => {
    if (field === 'doc_number') setDocNumber(value)
    else if (field === 'date') setDocDate(value)
    else if (field === 'include_invoice') setIncludeInvoice(value)
    else if (field === 'include_address_label') setIncludeAddressLabel(value)
    else if (field === 'address_format') setAddressFormat(value)
    else if (field === 'invoice_format') setInvoiceFormat(value)
    else if (field === 'weight') setWeight(value)
    else if (field === 'awb_number') setInvoiceAwbNumber(value)
    else if (field === 'contents_description') setInvoiceContentsDescription(value)
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] flex flex-col font-sans transition-colors duration-200">
      {/* Top Bar Header with Dot-Matrix Logo & Theme Switcher */}
      <Header theme={theme} onToggleTheme={handleToggleTheme} />

      {/* Main Container */}
      <main className="mx-auto w-full max-w-[1400px] flex-1 px-4 py-4 sm:px-8 lg:px-12">
        {/* Segmented Pill Navigation */}
        <SegmentedNav activeTab={activeTab} onSelectTab={handleSelectTab} />

        {/* Tab Content Surface */}
        <div key={activeTab} className="tab-content-enter mt-3 space-y-4">
          {/* Interactive OCR Review Modal if OCR was just executed */}
          {pendingOcrData && (
            <AddressReviewModal
              initialSender={pendingOcrData.sender}
              initialCustomer={pendingOcrData.customer}
              rawText={pendingOcrData.raw_text}
              onConfirm={handleConfirmOcr}
              onCancel={() => setPendingOcrData(null)}
            />
          )}

          {/* Invoice Tab */}
          {activeTab === 'invoice' && (
            invoiceViewMode === 'list' ? (
              <DocumentHistoryView
                defaultFilter="invoice"
                title="SAVED INVOICES"
                newButtonLabel="NEW INVOICE"
                onNewClick={handleNewInvoice}
                onLoadDocument={(doc) => {
                  handleLoadDocumentFromHistory(doc)
                  setInvoiceViewMode('form')
                }}
                onNotify={triggerToast}
              />
            ) : (
              <div className="space-y-4">
                {/* Back to Saved Invoices Bar */}
                <div className="flex items-center justify-between pb-1 border-b border-[var(--border-color)]">
                  <button
                    type="button"
                    onClick={() => setInvoiceViewMode('list')}
                    className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer font-mono-tech"
                  >
                    <ArrowLeft className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                    <span>BACK TO SAVED INVOICES</span>
                  </button>
                  <span className="font-mono-tech text-xs text-[var(--accent-red)] font-bold">
                    NEW INVOICE &bull; {docNumber}
                  </span>
                </div>

                {/* Single-Photo Address OCR Dropzone & Address Details (Hidden while reviewing OCR) */}
                {!pendingOcrData && (
                  <>
                    <AddressImageUpload
                      onAddressesExtracted={handleAddressesExtracted}
                      onNotify={triggerToast}
                    />

                    {/* Address Details (Sender & Customer) */}
                    <AddressDetailsCard
                      sender={sender}
                      customer={customer}
                      onUpdateSender={handleUpdateSender}
                      onUpdateCustomer={handleUpdateCustomer}
                    />
                  </>
                )}

                {/* Voice Input Section */}
                <VoiceItemInput
                  onAddItem={handleAddItemFromVoice}
                  onNotify={triggerToast}
                />

                {/* Manual Item Table Section */}
                <ManualItemTable
                  items={items}
                  onUpdateItem={handleUpdateItem}
                  onAddItem={handleAddBlankRow}
                  onRemoveItem={handleRemoveItem}
                  customTotal={customTotal}
                  onUpdateCustomTotal={handleUpdateCustomTotal}
                  isManualTotalEdited={isManualTotalEdited}
                  onResetAutoTotal={handleResetAutoTotal}
                />

                {/* Document Download Card with Themed NothingDatePicker */}
                <DocumentDownloadCard
                  mode="invoice"
                  payload={downloadPayload}
                  addressNumber={addressNumber}
                  onUpdateField={handleUpdateDownloadField}
                  onNotify={triggerToast}
                  onAddressSuccess={() => {
                    fetchNextDocNumber('address')
                    triggerToast(`Address Label ${addressNumber} saved to Address archive`)
                  }}
                  onSuccess={() => {
                    fetchNextDocNumber('invoice')
                    if (downloadPayload.include_address_label) {
                      fetchNextDocNumber('address')
                    }
                    setInvoiceViewMode('list')
                  }}
                />
              </div>
            )
          )}

          {/* Address Label Tab */}
          {activeTab === 'address' && (
            addressViewMode === 'list' ? (
              <DocumentHistoryView
                defaultFilter="address"
                title="SAVED ADDRESS LABELS"
                newButtonLabel="NEW ADDRESS LABEL"
                onNewClick={handleNewAddress}
                onLoadDocument={(doc) => {
                  handleLoadDocumentFromHistory(doc)
                  setAddressViewMode('form')
                }}
                onNotify={triggerToast}
              />
            ) : (
              <div className="space-y-4">
                {/* Back to Saved Address Labels Bar */}
                <div className="flex items-center justify-between pb-1 border-b border-[var(--border-color)]">
                  <button
                    type="button"
                    onClick={() => setAddressViewMode('list')}
                    className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer font-mono-tech"
                  >
                    <ArrowLeft className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                    <span>BACK TO SAVED ADDRESS LABELS</span>
                  </button>
                  <span className="font-mono-tech text-xs text-[var(--accent-red)] font-bold">
                    NEW ADDRESS LABEL &bull; {addressNumber}
                  </span>
                </div>

                {!pendingOcrData && (
                  <>
                    <AddressImageUpload
                      onAddressesExtracted={handleAddressesExtracted}
                      onNotify={triggerToast}
                    />
                    <AddressDetailsCard
                      sender={sender}
                      customer={customer}
                      onUpdateSender={handleUpdateSender}
                      onUpdateCustomer={handleUpdateCustomer}
                    />
                  </>
                )}
                <DocumentDownloadCard
                  mode="address"
                  payload={{
                    ...downloadPayload,
                    doc_number: addressNumber,
                    include_address_label: true,
                    include_invoice: false,
                  }}
                  onUpdateField={(field, val) => {
                    if (field === 'doc_number') {
                      setAddressNumber(val)
                    } else {
                      handleUpdateDownloadField(field, val)
                    }
                  }}
                  onNotify={triggerToast}
                  onSuccess={() => {
                    fetchNextDocNumber('address')
                    setAddressViewMode('list')
                  }}
                />
              </div>
            )
          )}

          {/* Booking AWB Tab */}
          {activeTab === 'booking' && (
            bookingViewMode === 'list' ? (
              <DocumentHistoryView
                defaultFilter="booking"
                title="SAVED BOOKING AWBS"
                newButtonLabel="NEW BOOKING AWB"
                onNewClick={handleNewBooking}
                onLoadDocument={(doc) => {
                  handleLoadDocumentFromHistory(doc)
                  setBookingViewMode('form')
                }}
                onNotify={triggerToast}
              />
            ) : (
              <div className="space-y-4">
                {/* Back to Saved Bookings Bar */}
                <div className="flex items-center justify-between pb-1 border-b border-[var(--border-color)]">
                  <button
                    type="button"
                    onClick={() => setBookingViewMode('list')}
                    className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer font-mono-tech"
                  >
                    <ArrowLeft className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                    <span>BACK TO SAVED BOOKINGS</span>
                  </button>
                  <span className="font-mono-tech text-xs text-emerald-400 font-bold">
                    NEW BOOKING AWB &bull; {awbNumber}
                  </span>
                </div>

                <BookingAwbCard
                  sender={sender}
                  customer={customer}
                  onUpdateSender={handleUpdateSender}
                  onUpdateCustomer={handleUpdateCustomer}
                  awbNumber={awbNumber}
                  onUpdateAwbNumber={setAwbNumber}
                  docDate={docDate}
                  onUpdateDocDate={setDocDate}
                  weight={weight}
                  onUpdateWeight={setWeight}
                  onNotify={triggerToast}
                  onSuccess={() => {
                    fetchNextDocNumber('booking')
                    setBookingViewMode('list')
                  }}
                />
              </div>
            )
          )}
        </div>
      </main>

      {/* Industrial Nothing OS Footer */}
      <footer className="mt-16 border-t border-[var(--border-color)] py-6 bg-[var(--bg-surface)]/50 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[var(--text-secondary)] font-mono-tech">
          <div className="flex items-center gap-2.5">
            <div className="grid grid-cols-3 gap-[2.5px] p-1 rounded bg-[var(--bg-card)] border border-[var(--border-color)] shadow-inner">
              <span className="h-1 w-1 rounded-full bg-[var(--accent-red)]" />
              <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
              <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
              <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
              <span className="h-1 w-1 rounded-full bg-[var(--accent-red)]" />
              <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
              <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
              <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
              <span className="h-1 w-1 rounded-full bg-[var(--accent-red)]" />
            </div>
            <span className="font-extrabold tracking-widest text-[var(--text-primary)]">SMARTINVOICE AI</span>
            <span className="text-[var(--text-muted)]">&bull; INDUSTRIAL WORKSPACE</span>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-[var(--text-muted)]">
            <span>HIGH-PRECISION BILLING & SHIPPING ENGINE</span>
          </div>
        </div>
      </footer>

      {/* Floating Confirmation Pill Toast */}
      <ToastBanner message={toastMessage} visible={showToast} />
    </div>
  )
}

export default App
