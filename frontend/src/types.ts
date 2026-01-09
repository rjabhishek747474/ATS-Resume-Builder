/**
 * TypeScript Types for ATS Resume Builder
 */

export type Screen = 'input' | 'review' | 'processing' | 'results';

export interface ResumeData {
    resumeId: string;
    sections: Record<string, string>;
    rawText: string;
}

export interface JDData {
    jdId: string;
    role: string;
    hardSkills: string[];
    softSkills: string[];
    keywords: { primary: string[]; secondary: string[] };
}

export interface OptimizationResult {
    optimizedResume: Record<string, string>;
    atsScore: number;
    improvements: string[];
    remainingGaps: string[];
}
