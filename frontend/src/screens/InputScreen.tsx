/**
 * Screen 1: Input
 * Upload resume + paste JD
 */

import { useState, useRef } from 'react';
import axios from 'axios';
import type { ResumeData, JDData } from '../types';

interface Props {
    onComplete: (resume: ResumeData, jd: JDData) => void;
}

export default function InputScreen({ onComplete }: Props) {
    const [resumeFile, setResumeFile] = useState<File | null>(null);
    const [resumeText, setResumeText] = useState('');
    const [jdText, setJDText] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setResumeFile(e.target.files[0]);
            setResumeText(''); // Clear text if file selected
        }
    };

    const handleSubmit = async () => {
        if (!resumeFile && !resumeText.trim()) {
            setError('Please upload a resume or paste text');
            return;
        }
        if (!jdText.trim()) {
            setError('Please paste a job description');
            return;
        }

        setLoading(true);
        setError('');

        try {
            // Upload resume
            let resumeResponse;
            if (resumeFile) {
                const formData = new FormData();
                formData.append('file', resumeFile);
                resumeResponse = await axios.post('/api/resume/upload', formData);
            } else {
                const formData = new FormData();
                formData.append('text', resumeText);
                resumeResponse = await axios.post('/api/resume/upload', formData);
            }

            // Extract JD
            const jdResponse = await axios.post('/api/jd/extract', {
                text: jdText,
            });

            // Pass data to next screen
            onComplete(
                {
                    resumeId: resumeResponse.data.resume_id,
                    sections: resumeResponse.data.sections,
                    rawText: resumeResponse.data.raw_text,
                },
                {
                    jdId: jdResponse.data.jd_id,
                    role: jdResponse.data.role,
                    hardSkills: jdResponse.data.hard_skills,
                    softSkills: jdResponse.data.soft_skills,
                    keywords: jdResponse.data.keywords,
                }
            );
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Something went wrong');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8">
            {/* Hero */}
            <div className="text-center space-y-2">
                <h2 className="text-3xl font-bold">Optimize Your Resume for ATS</h2>
                <p className="text-slate-400">
                    Upload your resume, paste the job description, get an ATS-optimized version.
                </p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400">
                    {error}
                </div>
            )}

            <div className="grid md:grid-cols-2 gap-6">
                {/* Resume Input */}
                <div className="bg-slate-800 rounded-xl p-6 space-y-4">
                    <h3 className="font-semibold text-lg">Resume</h3>

                    {/* File Upload */}
                    <div
                        onClick={() => fileInputRef.current?.click()}
                        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition
              ${resumeFile
                                ? 'border-green-500 bg-green-500/10'
                                : 'border-slate-600 hover:border-blue-500 hover:bg-slate-700/50'
                            }`}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.txt"
                            onChange={handleFileChange}
                            className="hidden"
                        />
                        {resumeFile ? (
                            <>
                                <div className="text-3xl mb-2">📄</div>
                                <p className="font-medium text-green-400">{resumeFile.name}</p>
                                <p className="text-sm text-slate-400 mt-1">Click to change</p>
                            </>
                        ) : (
                            <>
                                <div className="text-3xl mb-2">📤</div>
                                <p className="font-medium">Upload Resume</p>
                                <p className="text-sm text-slate-400 mt-1">PDF or TXT</p>
                            </>
                        )}
                    </div>

                    <div className="text-center text-slate-500 text-sm">— OR —</div>

                    {/* Text Paste */}
                    <textarea
                        value={resumeText}
                        onChange={(e) => {
                            setResumeText(e.target.value);
                            if (e.target.value) setResumeFile(null);
                        }}
                        placeholder="Paste resume text here..."
                        className="w-full h-40 bg-slate-700 rounded-lg p-4 text-sm resize-none
              placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {/* JD Input */}
                <div className="bg-slate-800 rounded-xl p-6 space-y-4">
                    <h3 className="font-semibold text-lg">Job Description</h3>

                    <textarea
                        value={jdText}
                        onChange={(e) => setJDText(e.target.value)}
                        placeholder="Paste the job description here...&#10;&#10;Include the full job listing with requirements and responsibilities."
                        className="w-full h-80 bg-slate-700 rounded-lg p-4 text-sm resize-none
              placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            {/* Submit Button */}
            <button
                onClick={handleSubmit}
                disabled={loading || (!resumeFile && !resumeText.trim()) || !jdText.trim()}
                className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 
          disabled:text-slate-500 rounded-xl font-semibold text-lg transition"
            >
                {loading ? (
                    <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Processing...
                    </span>
                ) : (
                    'Analyze Resume →'
                )}
            </button>
        </div>
    );
}
