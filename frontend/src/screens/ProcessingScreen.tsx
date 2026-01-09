/**
 * Screen 3: Processing
 * Show optimization progress
 */

import { useEffect, useState } from 'react';
import axios from 'axios';
import type { OptimizationResult } from '../types';

interface Props {
    resumeId: string;
    jdId: string;
    onComplete: (jobId: string, result: OptimizationResult) => void;
}

const STEPS = [
    { id: 'analyzing', label: 'Analyzing gaps', icon: '🔍' },
    { id: 'rewriting', label: 'Rewriting bullets', icon: '✏️' },
    { id: 'scoring', label: 'Calculating ATS score', icon: '📊' },
    { id: 'complete', label: 'Complete', icon: '✅' },
];

export default function ProcessingScreen({ resumeId, jdId, onComplete }: Props) {
    const [currentStep, setCurrentStep] = useState(0);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState('');

    useEffect(() => {
        startOptimization();
    }, []);

    const startOptimization = async () => {
        try {
            // Start optimization job
            const startRes = await axios.post('/api/optimize', {
                resume_id: resumeId,
                jd_id: jdId,
            });

            const jobId = startRes.data.job_id;

            // Poll for status
            let attempts = 0;
            while (attempts < 60) {
                await new Promise(resolve => setTimeout(resolve, 500));

                const statusRes = await axios.get(`/api/job/${jobId}/status`);
                const status = statusRes.data;

                setProgress(status.progress || 0);

                // Update step based on progress
                if (status.progress < 30) setCurrentStep(0);
                else if (status.progress < 70) setCurrentStep(1);
                else if (status.progress < 100) setCurrentStep(2);
                else setCurrentStep(3);

                if (status.status === 'completed') {
                    // Get result
                    const resultRes = await axios.get(`/api/job/${jobId}/result`);
                    const result = resultRes.data;

                    onComplete(jobId, {
                        optimizedResume: result.optimized_resume,
                        atsScore: result.ats_score,
                        improvements: result.improvements || [],
                        remainingGaps: result.remaining_gaps || [],
                    });
                    return;
                }

                if (status.status === 'failed') {
                    throw new Error(status.error || 'Optimization failed');
                }

                attempts++;
            }

            throw new Error('Optimization timeout');
        } catch (err: any) {
            setError(err.message || 'Something went wrong');
        }
    };

    if (error) {
        return (
            <div className="text-center py-16">
                <div className="text-5xl mb-4">❌</div>
                <h2 className="text-xl font-bold text-red-400 mb-2">Optimization Failed</h2>
                <p className="text-slate-400">{error}</p>
            </div>
        );
    }

    return (
        <div className="max-w-md mx-auto py-12 space-y-8">
            {/* Progress Circle */}
            <div className="relative w-32 h-32 mx-auto">
                <svg className="w-full h-full transform -rotate-90">
                    <circle
                        cx="64"
                        cy="64"
                        r="56"
                        fill="none"
                        stroke="#334155"
                        strokeWidth="8"
                    />
                    <circle
                        cx="64"
                        cy="64"
                        r="56"
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${progress * 3.52} 352`}
                        className="transition-all duration-300"
                    />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold">{progress}%</span>
                </div>
            </div>

            {/* Steps */}
            <div className="space-y-3">
                {STEPS.map((step, index) => (
                    <div
                        key={step.id}
                        className={`flex items-center gap-3 p-3 rounded-lg transition
              ${index < currentStep
                                ? 'bg-green-500/10 text-green-400'
                                : index === currentStep
                                    ? 'bg-blue-500/10 text-blue-400'
                                    : 'text-slate-500'
                            }`}
                    >
                        <span className="text-xl">{step.icon}</span>
                        <span className="font-medium">{step.label}</span>
                        {index === currentStep && index < STEPS.length - 1 && (
                            <svg className="ml-auto animate-spin h-4 w-4" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                        )}
                        {index < currentStep && (
                            <span className="ml-auto">✓</span>
                        )}
                    </div>
                ))}
            </div>

            {/* Info */}
            <p className="text-center text-sm text-slate-500">
                AI is optimizing your resume while preserving factual accuracy.
            </p>
        </div>
    );
}
