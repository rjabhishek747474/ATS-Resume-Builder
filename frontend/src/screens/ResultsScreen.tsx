/**
 * Screen 4: Results
 * Optimized resume + ATS score + PDF/DOCX download
 */

import { useState } from 'react';
import axios from 'axios';
import type { OptimizationResult } from '../types';

interface Props {
    result: OptimizationResult;
    jobId: string;
    onStartOver: () => void;
}

export default function ResultsScreen({ result, jobId, onStartOver }: Props) {
    const [activeTab, setActiveTab] = useState<'resume' | 'analysis'>('resume');
    const [downloading, setDownloading] = useState(false);

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-400';
        if (score >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getScoreLabel = (score: number) => {
        if (score >= 80) return 'Excellent Match';
        if (score >= 60) return 'Good Match';
        if (score >= 40) return 'Needs Improvement';
        return 'Poor Match';
    };

    const handleDownload = async (format: 'pdf' | 'docx') => {
        setDownloading(true);
        try {
            const response = await axios.post('/api/resume/download',
                { job_id: jobId, format },
                { responseType: 'blob' }
            );

            const blob = new Blob([response.data]);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `optimized-resume.${format}`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Download failed:', err);
        }
        setDownloading(false);
    };

    return (
        <div className="space-y-6">
            {/* Score Card */}
            <div className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-2xl p-8 text-center">
                <p className="text-slate-400 mb-2">ATS Compatibility Score</p>
                <p className={`text-6xl font-bold ${getScoreColor(result.atsScore)}`}>
                    {result.atsScore}
                </p>
                <p className="text-slate-400">/100</p>
                <p className={`mt-2 font-medium ${getScoreColor(result.atsScore)}`}>
                    {getScoreLabel(result.atsScore)}
                </p>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 bg-slate-800 rounded-lg p-1">
                <button
                    onClick={() => setActiveTab('resume')}
                    className={`flex-1 py-2 rounded-md font-medium transition
            ${activeTab === 'resume' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
                >
                    📄 Optimized Resume
                </button>
                <button
                    onClick={() => setActiveTab('analysis')}
                    className={`flex-1 py-2 rounded-md font-medium transition
            ${activeTab === 'analysis' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
                >
                    📊 Analysis
                </button>
            </div>

            {/* Content */}
            {activeTab === 'resume' ? (
                <div className="space-y-4">
                    {Object.entries(result.optimizedResume).map(([section, content]) => (
                        content && (
                            <div key={section} className="bg-slate-800 rounded-xl p-6">
                                <h3 className="font-semibold text-lg mb-3 capitalize">
                                    {section}
                                </h3>
                                <pre className="whitespace-pre-wrap font-sans text-slate-300 text-sm leading-relaxed">
                                    {content}
                                </pre>
                            </div>
                        )
                    ))}
                </div>
            ) : (
                <div className="space-y-4">
                    {/* Improvements */}
                    {result.improvements.length > 0 && (
                        <div className="bg-slate-800 rounded-xl p-6">
                            <h3 className="font-semibold text-lg mb-3 text-green-400">
                                ✅ Improvements Made
                            </h3>
                            <ul className="space-y-2">
                                {result.improvements.map((item, i) => (
                                    <li key={i} className="flex items-start gap-2 text-slate-300">
                                        <span className="text-green-400">+</span>
                                        <span>{item.replace(/^\+\s*/, '')}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Remaining Gaps */}
                    {result.remainingGaps.length > 0 && (
                        <div className="bg-slate-800 rounded-xl p-6">
                            <h3 className="font-semibold text-lg mb-3 text-amber-400">
                                ⚠️ Remaining Gaps
                            </h3>
                            <ul className="space-y-2">
                                {result.remainingGaps.map((item, i) => (
                                    <li key={i} className="flex items-start gap-2 text-slate-300">
                                        <span className="text-amber-400">-</span>
                                        <span>{typeof item === 'string' ? item.replace(/^-\s*/, '') : JSON.stringify(item)}</span>
                                    </li>
                                ))}
                            </ul>
                            <p className="text-sm text-slate-500 mt-4">
                                These gaps cannot be filled without adding new experience or skills.
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
                <button
                    onClick={onStartOver}
                    className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
                >
                    ← Start Over
                </button>
                <button
                    onClick={() => handleDownload('pdf')}
                    disabled={downloading}
                    className="flex-1 py-3 bg-red-600 hover:bg-red-500 disabled:bg-slate-600 rounded-lg font-semibold transition flex items-center justify-center gap-2"
                >
                    📄 Download PDF
                </button>
                <button
                    onClick={() => handleDownload('docx')}
                    disabled={downloading}
                    className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 rounded-lg font-semibold transition flex items-center justify-center gap-2"
                >
                    📝 Download DOCX
                </button>
            </div>
        </div>
    );
}
