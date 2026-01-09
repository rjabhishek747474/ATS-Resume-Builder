/**
 * ATS Resume Builder - Main App
 * 
 * 4 Screen flow:
 * 1. Input - Upload resume + paste JD
 * 2. Review - Edit parsed sections
 * 3. Processing - Show optimization progress
 * 4. Results - Optimized resume + score
 */

import { useState } from 'react';
import InputScreen from './screens/InputScreen';
import ReviewScreen from './screens/ReviewScreen';
import ProcessingScreen from './screens/ProcessingScreen';
import ResultsScreen from './screens/ResultsScreen';
import type { Screen, ResumeData, JDData, OptimizationResult } from './types';

// Re-export types for backward compatibility
export type { Screen, ResumeData, JDData, OptimizationResult };

function App() {
  const [screen, setScreen] = useState<Screen>('input');
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [jdData, setJDData] = useState<JDData | null>(null);
  const [jobId, setJobId] = useState<string>('');
  const [result, setResult] = useState<OptimizationResult | null>(null);

  const handleInputComplete = (resume: ResumeData, jd: JDData) => {
    setResumeData(resume);
    setJDData(jd);
    setScreen('review');
  };

  const handleReviewComplete = (updatedSections: Record<string, string>) => {
    if (resumeData) {
      setResumeData({ ...resumeData, sections: updatedSections });
    }
    setScreen('processing');
  };

  const handleProcessingComplete = (jobId: string, optimizationResult: OptimizationResult) => {
    setJobId(jobId);
    setResult(optimizationResult);
    setScreen('results');
  };

  const handleStartOver = () => {
    setScreen('input');
    setResumeData(null);
    setJDData(null);
    setJobId('');
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">
            📄 ATS Resume Builder
          </h1>
          {screen !== 'input' && (
            <button
              onClick={handleStartOver}
              className="text-sm text-slate-400 hover:text-white transition"
            >
              Start Over
            </button>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {screen === 'input' && (
          <InputScreen onComplete={handleInputComplete} />
        )}

        {screen === 'review' && resumeData && jdData && (
          <ReviewScreen
            resumeData={resumeData}
            jdData={jdData}
            onComplete={handleReviewComplete}
            onBack={() => setScreen('input')}
          />
        )}

        {screen === 'processing' && resumeData && jdData && (
          <ProcessingScreen
            resumeId={resumeData.resumeId}
            jdId={jdData.jdId}
            onComplete={handleProcessingComplete}
          />
        )}

        {screen === 'results' && result && (
          <ResultsScreen
            result={result}
            jobId={jobId}
            onStartOver={handleStartOver}
          />
        )}
      </main>
    </div>
  );
}

export default App;
