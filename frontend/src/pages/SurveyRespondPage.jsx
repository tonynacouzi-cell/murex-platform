// SurveyRespondPage.jsx — public page for survey respondents
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { surveysApi } from '../api/client'
import toast from 'react-hot-toast'

export function SurveyRespondPage() {
  const { token } = useParams()
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const formattedAnswers = Object.entries(answers).map(([qId, val]) => ({
        question_id: parseInt(qId),
        value_numeric: typeof val === 'number' ? val : null,
        value_text: typeof val === 'string' ? val : null,
      }))
      await surveysApi.respond(token, { token, answers: formattedAnswers })
      setSubmitted(true)
    } catch { toast.error('Submission failed. Please try again.') }
    finally { setLoading(false) }
  }

  if (submitted) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-8 text-center max-w-md w-full shadow-sm border border-gray-100">
        <div className="text-4xl mb-4">🎉</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Thank you!</h2>
        <p className="text-gray-500 text-sm">Your feedback has been submitted successfully.</p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-8 max-w-xl w-full shadow-sm border border-gray-100">
        <h2 className="text-lg font-bold text-gray-900 mb-6">Share Your Feedback</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              How likely are you to recommend us? (0–10)
            </label>
            <div className="flex gap-2 flex-wrap">
              {Array.from({length: 11}, (_, i) => (
                <button
                  key={i} type="button"
                  onClick={() => setAnswers({...answers, nps: i})}
                  className={`w-10 h-10 rounded-lg text-sm font-medium border transition-colors ${
                    answers.nps === i
                      ? 'bg-[#1E3A5F] text-white border-[#1E3A5F]'
                      : 'border-gray-200 text-gray-600 hover:border-[#1E3A5F]'
                  }`}
                >{i}</button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Any comments? (Optional)
            </label>
            <textarea
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={answers.comment || ''}
              onChange={e => setAnswers({...answers, comment: e.target.value})}
              placeholder="Share your thoughts..."
            />
          </div>
          <button
            type="submit"
            disabled={loading || answers.nps === undefined}
            className="w-full bg-[#1E3A5F] text-white rounded-lg py-2.5 text-sm font-medium disabled:opacity-50 hover:bg-[#162d4a] transition-colors"
          >
            {loading ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </form>
      </div>
    </div>
  )
}
export default SurveyRespondPage
