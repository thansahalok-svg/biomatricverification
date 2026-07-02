import React, { useEffect, useState } from 'react'
import { attendanceAPI } from '../services/api'

export default function StudentAttendanceHistory() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const res = await attendanceAPI.getHistory()
      setRecords(res.data.attendance_records || [])
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Unable to load attendance history', 'error')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => setMessage(''), 5000)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-5xl mx-auto card">
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="navbar-brand text-2xl">Attendance History</h1>
            <p className="text-gray-600 mt-2">Your recorded attendance entries.</p>
          </div>
          <a href="/student/dashboard" className="btn btn-secondary">Back to Dashboard</a>
        </div>

        {message && <div className={`alert alert-${messageType} mb-4`}>{message}</div>}

        {records.length === 0 ? (
          <div className="alert alert-info">No attendance records found yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="py-3 px-2">Date</th>
                  <th className="py-3 px-2">Check-in Time</th>
                  <th className="py-3 px-2">Status</th>
                  <th className="py-3 px-2">Method</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.attendance_id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-2">{record.date}</td>
                    <td className="py-3 px-2">{record.check_in_time}</td>
                    <td className="py-3 px-2">
                      <span className={`px-2 py-1 rounded text-sm ${record.status === 'present' || record.status === 'late' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {record.status}
                      </span>
                    </td>
                    <td className="py-3 px-2">{record.verification_method}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
