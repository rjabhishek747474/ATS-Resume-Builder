/**
 * Screen 2: Review
 * Edit parsed resume sections
 */

import { useState } from 'react';
import type { ResumeData, JDData } from '../types';

interface Props {
    resumeData: ResumeData;
    jdData: JDData;
    onComplete: (sections: Record<string, string>) => void;
    onBack: () => void;
}

export default function ReviewScreen({ resumeData, jdData, onComplete, onBack }: Props) {
    const [sections, setSections] = useState(resumeData.sections);
    const [activeSection, setActiveSection] = useState<string | null>(null);

    const sectionLabels: Record<string, string> = {
        summary: '📝 Summary',
        experience: '💼 Experience',
        skills: '🔧 Skills',
        education: '🎓 Education',
        projects: '📁 Projects',
        certifications: '📜 Certifications',
    };

    const handleSectionChange = (key: string, value: string) => {
        setSections(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Review Parsed Resume</h2>
                    <p className="text-slate-400">
                        Verify sections are correctly detected. Edit if needed.
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-sm text-slate-400">Target Role</p>
                    <p className="font-semibold text-blue-400">{jdData.role}</p>
                </div>
            </div>

            {/* JD Skills Preview */}
            <div className="bg-slate-800/50 rounded-lg p-4">
                <p className="text-sm text-slate-400 mb-2">Key skills from JD:</p>
                <div className="flex flex-wrap gap-2">
                    {jdData.hardSkills.slice(0, 10).map((skill, i) => (
                        <span
                            key={i}
                            className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-sm"
                        >
                            {skill}
                        </span>
                    ))}
                </div>
            </div>

            {/* Sections */}
            <div className="space-y-4">
                {Object.entries(sections).map(([key, content]) => (
                    <div
                        key={key}
                        className="bg-slate-800 rounded-xl overflow-hidden"
                    >
                        <button
                            onClick={() => setActiveSection(activeSection === key ? null : key)}
                            className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-700/50 transition"
                        >
                            <span className="font-medium">
                                {sectionLabels[key] || key.charAt(0).toUpperCase() + key.slice(1)}
                            </span>
                            <span className="text-slate-400">
                                {content ? `${content.split('\n').length} lines` : 'Empty'}
                                <span className="ml-2">{activeSection === key ? '▼' : '▶'}</span>
                            </span>
                        </button>

                        {activeSection === key && (
                            <div className="px-6 pb-4">
                                <textarea
                                    value={content}
                                    onChange={(e) => handleSectionChange(key, e.target.value)}
                                    className="w-full h-48 bg-slate-700 rounded-lg p-4 text-sm resize-none
                    font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                {!content && (
                                    <p className="text-amber-400 text-sm mt-2">
                                        ⚠️ This section is empty. Consider adding content.
                                    </p>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Actions */}
            <div className="flex gap-4">
                <button
                    onClick={onBack}
                    className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
                >
                    ← Back
                </button>
                <button
                    onClick={() => onComplete(sections)}
                    className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold transition"
                >
                    Optimize Resume →
                </button>
            </div>
        </div>
    );
}
