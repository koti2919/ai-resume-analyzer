import { useEffect, useState } from "react";
import "./App.css";
import ReportDownload from "./components/ReportDownload";

const analysisSteps = [
  "Extracting resume text",
  "Detecting resume sections",
  "Extracting skills",
  "Comparing job requirements",
  "Checking ATS keywords",
  "Evaluating resume quality",
  "Generating improvement recommendations",
];

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysisStep, setAnalysisStep] = useState(0);

  useEffect(() => {
    if (!loading) return;

    const interval = setInterval(() => {
      setAnalysisStep((currentStep) => {
        if (currentStep < analysisSteps.length - 1) {
          return currentStep + 1;
        }

        return currentStep;
      });
    }, 700);

    return () => clearInterval(interval);
  }, [loading]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    if (file.type !== "application/pdf") {
      setError("Please upload a PDF resume.");
      setResumeFile(null);
      return;
    }

    setResumeFile(file);
    setError("");
    setResult(null);
    setAnalysisStep(0);
  };

  const handleAnalyze = async () => {
    if (!resumeFile) {
      setError("Please upload your resume PDF.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setAnalysisStep(0);

    try {
      const formData = new FormData();

      formData.append("file", resumeFile);
      formData.append("job_description", jobDescription);

      const response = await fetch(
        "https://ai-resume-analyzer-kggz.onrender.com/analyze-resume",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          `Server returned ${response.status}: ${errorText}`
        );
      }

      const data = await response.json();

      setAnalysisStep(analysisSteps.length);
      setResult(data);
    } catch (error) {
      console.error("Analysis error:", error);

      setError(
        "Unable to connect to the FastAPI backend. Make sure the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 80) return "score-good";
    if (score >= 60) return "score-medium";

    return "score-low";
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";

    return "Needs Improvement";
  };

  const getSafeScore = (score) => {
    const numericScore = Number(score);

    if (Number.isNaN(numericScore)) {
      return 0;
    }

    return Math.max(0, Math.min(100, numericScore));
  };

  const renderList = (items, emptyText = "None") => {
    if (!items || items.length === 0) {
      return (
        <span className="empty-text">
          {emptyText}
        </span>
      );
    }

    return (
      <div className="tag-list">
        {items.map((item, index) => (
          <span
            className="skill-tag"
            key={`${item}-${index}`}
          >
            {typeof item === "string"
              ? item
              : item.recommendation ||
                item.description ||
                JSON.stringify(item)}
          </span>
        ))}
      </div>
    );
  };

  const ScoreCard = ({
    title,
    score,
    subtitle,
  }) => {
    const safeScore = getSafeScore(score);

    return (
      <div className="score-card professional-score-card">
        <div className="score-card-top">
          <span className="score-label">
            {title}
          </span>

          <span
            className={`score-mini-status ${getScoreClass(
              safeScore
            )}`}
          >
            {getScoreLabel(safeScore)}
          </span>
        </div>

        <div className="score-visual">
          <div
            className={`score-circle ${getScoreClass(
              safeScore
            )}`}
            style={{
              "--score": `${safeScore * 3.6}deg`,
            }}
          >
            <div className="score-circle-inner">
              <strong>
                {score ?? "N/A"}
              </strong>

              <small>/ 100</small>
            </div>
          </div>

          <div className="score-description">
            <strong>{subtitle}</strong>

            <div className="score-progress">
              <div
                className={`score-progress-fill ${getScoreClass(
                  safeScore
                )}`}
                style={{
                  width: `${safeScore}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const atsScore =
    result?.overall_ats?.ats_score ?? 0;

  const jobMatch =
    result?.skill_matching
      ?.weighted_match_percentage ?? 0;

  const resumeHealth =
    result?.step_39_resume_health
      ?.health_score ?? 0;

  const contentScore =
    result?.overall_ats
      ?.ats_breakdown
      ?.content_score ?? 0;

  const improvementPlan =
    result?.step_34_improvement_plan;

  const highPriority =
    improvementPlan?.high_priority || [];

  const mediumPriority =
    improvementPlan?.medium_priority || [];

  const lowPriority =
    improvementPlan?.low_priority || [];

  const hasImprovementItems =
    highPriority.length > 0 ||
    mediumPriority.length > 0 ||
    lowPriority.length > 0;

  const renderImprovementItem = (
    item,
    index
  ) => {
    if (typeof item === "string") {
      return (
        <div
          className="improvement-item"
          key={`${item}-${index}`}
        >
          <span>{index + 1}</span>

          <p>{item}</p>
        </div>
      );
    }

    return (
      <div
        className="improvement-item"
        key={index}
      >
        <span>{index + 1}</span>

        <p>
          {item?.recommendation ||
            item?.description ||
            item?.message ||
            JSON.stringify(item)}
        </p>
      </div>
    );
  };

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">
        <div className="header-content">
          <div>
            <p className="eyebrow">
              AI POWERED CAREER TOOL
            </p>

            <h1>
              AI Resume Analyzer
            </h1>

            <p className="header-description">
              Analyze your resume, match job
              requirements, identify skill gaps,
              and improve your resume.
            </p>
          </div>
        </div>
      </header>

      <main className="container">

        {/* INPUT SECTION */}

        <section className="input-section">

          <div className="input-card">

            <div className="section-heading">
              <span className="section-number">
                01
              </span>

              <div>
                <h2>
                  Upload Your Resume
                </h2>

                <p>
                  Upload your resume in PDF format.
                </p>
              </div>
            </div>

            <label
              className={`upload-box ${
                resumeFile
                  ? "upload-box-selected"
                  : ""
              }`}
            >
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
              />

              <div className="upload-icon">
                ↑
              </div>

              <strong>
                {resumeFile
                  ? resumeFile.name
                  : "Choose your resume"}
              </strong>

              <span>
                {resumeFile
                  ? "PDF selected successfully"
                  : "PDF files only"}
              </span>
            </label>

          </div>

          <div className="input-card">

            <div className="section-heading">
              <span className="section-number">
                02
              </span>

              <div>
                <h2>
                  Job Description
                </h2>

                <p>
                  Paste the job description you
                  want to compare against.
                </p>
              </div>
            </div>

            <textarea
              className="job-description-input"
              value={jobDescription}
              onChange={(event) =>
                setJobDescription(
                  event.target.value
                )
              }
              placeholder="Paste the job description here..."
              rows={10}
            />

          </div>

          {error && (
            <div className="error-message">
              <span>!</span>
              {error}
            </div>
          )}

          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="button-spinner"></span>
                Analyzing Resume...
              </>
            ) : (
              <>
                Analyze Resume
                <span>→</span>
              </>
            )}
          </button>

        </section>

        {/* ANALYSIS PROGRESS */}

        {loading && (
          <section className="progress-card">

            <div className="progress-header">

              <div>
                <p className="eyebrow">
                  ANALYSIS IN PROGRESS
                </p>

                <h2>
                  Analyzing your resume
                </h2>
              </div>

              <span className="progress-percent">
                {Math.min(
                  100,
                  Math.round(
                    ((analysisStep + 1) /
                      analysisSteps.length) *
                      100
                  )
                )}
                %
              </span>

            </div>

            <div className="analysis-progress-track">
              <div
                className="analysis-progress-fill"
                style={{
                  width: `${Math.min(
                    100,
                    ((analysisStep + 1) /
                      analysisSteps.length) *
                      100
                  )}%`,
                }}
              ></div>
            </div>

            <div className="analysis-steps">
              {analysisSteps.map(
                (step, index) => (
                  <div
                    className={`analysis-step ${
                      index <= analysisStep
                        ? "analysis-step-active"
                        : ""
                    }`}
                    key={step}
                  >
                    <span className="step-check">
                      {index < analysisStep
                        ? "✓"
                        : index === analysisStep
                        ? "•"
                        : ""}
                    </span>

                    <span>
                      {step}
                    </span>
                  </div>
                )
              )}
            </div>

          </section>
        )}

        {/* RESULTS */}

        {result && (
          <section className="results">

            {/* RESULTS HEADER */}

            <div className="results-header">

              <div>
                <p className="eyebrow">
                  ANALYSIS COMPLETE
                </p>

                <h2>
                  Resume Analysis Report
                </h2>

                <p>
                  Results generated from your
                  resume and the provided job
                  description.
                </p>
              </div>

              {/* ONLY STATUS HERE */}
              <div className="results-header-actions">

                <div className="result-status">
                  {result
                    .step_40_analysis_summary
                    ?.overall_status ||
                    "Analysis Complete"}
                </div>

              </div>

            </div>

            {/* =================================================
                REPORT DOWNLOAD
                IMPORTANT:
                ReportDownload is now OUTSIDE the header.
                It gets the full width of .results.
                ================================================= */}

            <div className="report-full-width">

              <ReportDownload
                result={result}
                atsScore={atsScore}
                jobMatch={jobMatch}
                resumeHealth={resumeHealth}
                contentScore={contentScore}
                skillMatching={
                  result?.skill_matching
                }
                resumeHealthData={
                  result?.step_39_resume_health
                }
                finalSummary={
                  result?.step_40_analysis_summary
                }
              />

            </div>

            {/* PROFESSIONAL SCORE DASHBOARD */}

            <section className="score-dashboard">

              <div className="dashboard-heading">

                <div>
                  <p className="eyebrow">
                    RESUME PERFORMANCE
                  </p>

                  <h2>
                    Professional Score Dashboard
                  </h2>
                </div>

              </div>

              <div className="score-grid">

                <ScoreCard
                  title="ATS Score"
                  score={atsScore}
                  subtitle="ATS compatibility"
                />

                <ScoreCard
                  title="Job Match"
                  score={jobMatch}
                  subtitle="Job requirement match"
                />

                <ScoreCard
                  title="Resume Health"
                  score={resumeHealth}
                  subtitle="Overall resume quality"
                />

                <ScoreCard
                  title="Content Score"
                  score={contentScore}
                  subtitle="Resume content quality"
                />

              </div>

            </section>

            {/* SKILL MATCH */}

            <div className="dashboard-card skill-match-dashboard">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    SKILL MATCH
                  </p>

                  <h2>
                    Job Skill Match
                  </h2>

                  <p>
                    Compare your resume skills
                    with the job requirements.
                  </p>
                </div>

              </div>

              <div className="skill-match-overview">

                <div className="skill-match-main">

                  <span className="skill-match-label">
                    Overall Job Match
                  </span>

                  <strong className="skill-match-percentage">
                    {jobMatch}%
                  </strong>

                  <div className="skill-match-track">

                    <div
                      className="skill-match-fill"
                      style={{
                        width: `${getSafeScore(
                          jobMatch
                        )}%`,
                      }}
                    ></div>

                  </div>

                </div>

                <div className="skill-match-stats">

                  <div className="skill-match-stat">
                    <span>
                      Required Matched
                    </span>

                    <strong>
                      {result
                        ?.skill_matching
                        ?.matched_required
                        ?.length || 0}
                    </strong>
                  </div>

                  <div className="skill-match-stat">
                    <span>
                      Required Missing
                    </span>

                    <strong>
                      {result
                        ?.skill_matching
                        ?.missing_required
                        ?.length || 0}
                    </strong>
                  </div>

                  <div className="skill-match-stat">
                    <span>
                      Preferred Matched
                    </span>

                    <strong>
                      {result
                        ?.skill_matching
                        ?.matched_preferred
                        ?.length || 0}
                    </strong>
                  </div>

                  <div className="skill-match-stat">
                    <span>
                      Preferred Missing
                    </span>

                    <strong>
                      {result
                        ?.skill_matching
                        ?.missing_preferred
                        ?.length || 0}
                    </strong>
                  </div>

                </div>

              </div>

              <div className="skill-category-section">

                <div className="skill-category-grid">

                  <div className="skill-panel">

                    <div className="skill-panel-title">
                      <span className="skill-status-icon matched-icon">
                        ✓
                      </span>

                      Required Skills Matched
                    </div>

                    {renderList(
                      result?.skill_matching
                        ?.matched_required,
                      "No required skills matched"
                    )}

                  </div>

                  <div className="skill-panel">

                    <div className="skill-panel-title">
                      <span className="skill-status-icon missing-icon">
                        !
                      </span>

                      Required Skills Missing
                    </div>

                    {renderList(
                      result?.skill_matching
                        ?.missing_required,
                      "No missing required skills"
                    )}

                  </div>

                  <div className="skill-panel">

                    <div className="skill-panel-title">
                      <span className="skill-status-icon matched-icon">
                        ✓
                      </span>

                      Preferred Skills Matched
                    </div>

                    {renderList(
                      result?.skill_matching
                        ?.matched_preferred,
                      "No preferred skills matched"
                    )}

                  </div>

                  <div className="skill-panel">

                    <div className="skill-panel-title">
                      <span className="skill-status-icon missing-icon">
                        !
                      </span>

                      Preferred Skills Missing
                    </div>

                    {renderList(
                      result?.skill_matching
                        ?.missing_preferred,
                      "No missing preferred skills"
                    )}

                  </div>

                </div>

              </div>

            </div>

            {/* SKILL GAP ANALYSIS */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    SKILL GAP ANALYSIS
                  </p>

                  <h2>
                    Skills You Can Improve
                  </h2>
                </div>

              </div>

              <div className="skill-gap-grid">

                {result?.skill_gaps?.length > 0 ? (
                  result.skill_gaps.map(
                    (gap, index) => (
                      <div
                        className="skill-gap-item"
                        key={`${gap}-${index}`}
                      >
                        <span>
                          {gap}
                        </span>
                      </div>
                    )
                  )
                ) : (
                  <span className="empty-text">
                    No major skill gaps detected.
                  </span>
                )}

              </div>

            </div>

            {/* ATS KEYWORD ANALYSIS */}

            <div className="dashboard-card ats-keyword-dashboard">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    ATS ANALYSIS
                  </p>

                  <h2>
                    ATS Keyword Analysis
                  </h2>

                  <p>
                    Check how well your resume
                    matches important job keywords.
                  </p>
                </div>

              </div>

              <div className="ats-overview">

                <div className="ats-main-card">

                  <span>
                    Keyword Match
                  </span>

                  <strong className="ats-percentage">
                    {result
                      ?.ats_keyword_analysis
                      ?.keyword_match_percentage ?? 0}
                    %
                  </strong>

                  <div className="ats-progress-track">

                    <div
                      className="ats-progress-fill"
                      style={{
                        width: `${getSafeScore(
                          result
                            ?.ats_keyword_analysis
                            ?.keyword_match_percentage
                        )}%`,
                      }}
                    ></div>

                  </div>

                </div>

                <div className="ats-stat-grid">

                  <div className="ats-stat-card">
                    <span>
                      Total Keywords
                    </span>

                    <strong>
                      {result
                        ?.ats_keyword_analysis
                        ?.total_keywords || 0}
                    </strong>
                  </div>

                  <div className="ats-stat-card">
                    <span>
                      Matched
                    </span>

                    <strong>
                      {result
                        ?.ats_keyword_analysis
                        ?.matched_keywords
                        ?.length || 0}
                    </strong>
                  </div>

                  <div className="ats-stat-card">
                    <span>
                      Missing
                    </span>

                    <strong>
                      {result
                        ?.ats_keyword_analysis
                        ?.missing_keywords
                        ?.length || 0}
                    </strong>
                  </div>

                </div>

              </div>

              <div className="ats-keyword-breakdown">

                <div className="ats-keyword-panel">

                  <div className="ats-panel-header">

                    <span className="ats-panel-icon ats-matched">
                      ✓
                    </span>

                    <div>
                      <strong>
                        Matched Keywords
                      </strong>

                      <span>
                        Keywords found in your resume
                      </span>
                    </div>

                  </div>

                  {renderList(
                    result
                      ?.ats_keyword_analysis
                      ?.matched_keywords,
                    "No matched keywords"
                  )}

                </div>

                <div className="ats-keyword-panel">

                  <div className="ats-panel-header">

                    <span className="ats-panel-icon ats-missing">
                      !
                    </span>

                    <div>
                      <strong>
                        Missing Keywords
                      </strong>

                      <span>
                        Keywords you can add
                      </span>
                    </div>

                  </div>

                  {renderList(
                    result
                      ?.ats_keyword_analysis
                      ?.missing_keywords,
                    "No missing keywords"
                  )}

                </div>

              </div>

              <div className="ats-recommendation">

                <strong>
                  ATS Optimization Tip
                </strong>

                <p>
                  Add relevant missing keywords
                  naturally to your skills,
                  projects, and experience
                  sections when they genuinely
                  reflect your abilities.
                </p>

              </div>

            </div>

            {/* RESUME QUALITY */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    RESUME QUALITY
                  </p>

                  <h2>
                    Resume Quality Analysis
                  </h2>
                </div>

              </div>

              <div className="quality-grid">

                <div className="quality-item">
                  <span>
                    Resume Structure
                  </span>

                  <strong>
                    {result?.resume_quality
                      ?.structure_quality ||
                      result?.resume_quality
                        ?.structure_score ||
                      "N/A"}
                  </strong>
                </div>

                <div className="quality-item">
                  <span>
                    Content Quality
                  </span>

                  <strong>
                    {result?.resume_quality
                      ?.content_score ??
                      contentScore}
                  </strong>
                </div>

                <div className="quality-item">
                  <span>
                    Projects
                  </span>

                  <strong>
                    {result?.resume_quality
                      ?.project_count ??
                      "N/A"}
                  </strong>
                </div>

                <div className="quality-item">
                  <span>
                    Resume Lines
                  </span>

                  <strong>
                    {result?.resume_quality
                      ?.total_lines ??
                      "N/A"}
                  </strong>
                </div>

              </div>

            </div>

            {/* SECTION SCORES */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    SECTION ANALYSIS
                  </p>

                  <h2>
                    Section-wise Resume Scores
                  </h2>
                </div>

              </div>

              <div className="section-score-grid">

                {result?.section_scores &&
                  Object.entries(
                    result.section_scores
                  ).map(
                    ([section, score]) => (
                      <div
                        className="section-score-item"
                        key={section}
                      >

                        <div className="section-score-top">

                          <span>
                            {section
                              .replaceAll("_", " ")
                              .replace(
                                /\b\w/g,
                                (letter) =>
                                  letter.toUpperCase()
                              )}
                          </span>

                          <strong>
                            {score}
                          </strong>

                        </div>

                        <div className="section-score-track">

                          <div
                            className="section-score-fill"
                            style={{
                              width: `${getSafeScore(
                                score
                              )}%`,
                            }}
                          ></div>

                        </div>

                      </div>
                    )
                  )}

              </div>

            </div>

            {/* JOB ROLE ALIGNMENT */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    JOB ROLE ALIGNMENT
                  </p>

                  <h2>
                    Role Alignment
                  </h2>
                </div>

              </div>

              <div className="role-alignment-card">

                <div className="role-alignment-icon">
                  ✓
                </div>

                <div>

                  <strong>
                    {result
                      ?.step_38_job_role_alignment
                      ?.alignment_status ||
                      "Role Alignment Detected"}
                  </strong>

                  <p>
                    {result
                      ?.step_38_job_role_alignment
                      ?.detected_role ||
                      "Software Developer"}
                  </p>

                </div>

              </div>

            </div>

            {/* RESUME HEALTH */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    RESUME HEALTH
                  </p>

                  <h2>
                    Resume Health Report
                  </h2>
                </div>

              </div>

              <div className="health-score-row">

                <div className="health-score-circle">

                  <strong>
                    {resumeHealth}
                  </strong>

                  <span>
                    / 100
                  </span>

                </div>

                <div>

                  <h3>
                    {getScoreLabel(
                      getSafeScore(resumeHealth)
                    )}
                  </h3>

                  <p>
                    Overall resume health based
                    on content, structure,
                    ATS compatibility, and
                    job alignment.
                  </p>

                </div>

              </div>

              <div className="health-columns">

                <div className="health-panel">

                  <h3>
                    Strengths
                  </h3>

                  {renderList(
                    result
                      ?.step_39_resume_health
                      ?.strengths,
                    "No strengths available"
                  )}

                </div>

                <div className="health-panel">

                  <h3>
                    Weaknesses
                  </h3>

                  {renderList(
                    result
                      ?.step_39_resume_health
                      ?.weaknesses,
                    "No weaknesses available"
                  )}

                </div>

              </div>

            </div>

            {/* IMPROVEMENT PLAN */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    IMPROVEMENT PLAN
                  </p>

                  <h2>
                    Resume Improvement Recommendations
                  </h2>
                </div>

              </div>

              <div className="improvement-summary">

                {improvementPlan
                  ?.recommendation_summary ||
                  "No improvement recommendations available."}

              </div>

              {hasImprovementItems ? (
                <div className="improvement-list">

                  {highPriority.length > 0 && (
                    <div className="improvement-priority-section">

                      <div className="improvement-priority-header high-priority-header">

                        <span className="priority-dot high-priority-dot"></span>

                        <h3>
                          High Priority
                        </h3>

                      </div>

                      <div className="improvement-items">

                        {highPriority.map(
                          (item, index) =>
                            renderImprovementItem(
                              item,
                              index
                            )
                        )}

                      </div>

                    </div>
                  )}

                  {mediumPriority.length > 0 && (
                    <div className="improvement-priority-section">

                      <div className="improvement-priority-header medium-priority-header">

                        <span className="priority-dot medium-priority-dot"></span>

                        <h3>
                          Medium Priority
                        </h3>

                      </div>

                      <div className="improvement-items">

                        {mediumPriority.map(
                          (item, index) =>
                            renderImprovementItem(
                              item,
                              index
                            )
                        )}

                      </div>

                    </div>
                  )}

                  {lowPriority.length > 0 && (
                    <div className="improvement-priority-section">

                      <div className="improvement-priority-header low-priority-header">

                        <span className="priority-dot low-priority-dot"></span>

                        <h3>
                          Low Priority
                        </h3>

                      </div>

                      <div className="improvement-items">

                        {lowPriority.map(
                          (item, index) =>
                            renderImprovementItem(
                              item,
                              index
                            )
                        )}

                      </div>

                    </div>
                  )}

                </div>
              ) : (
                <div className="empty-text">
                  No detailed improvement recommendations available.
                </div>
              )}

            </div>

            {/* BULLET ANALYSIS */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    BULLET ANALYSIS
                  </p>

                  <h2>
                    Resume Bullet & Action-Verb Analysis
                  </h2>
                </div>

              </div>

              <div className="analysis-stat-grid">

                <div className="analysis-stat">

                  <span>
                    Score
                  </span>

                  <strong>
                    {result
                      ?.step_35_bullet_analysis
                      ?.score ??
                      "N/A"}
                  </strong>

                </div>

                <div className="analysis-stat">

                  <span>
                    Total Bullets
                  </span>

                  <strong>
                    {result
                      ?.step_35_bullet_analysis
                      ?.total_bullets ??
                      "N/A"}
                  </strong>

                </div>

                <div className="analysis-stat">

                  <span>
                    Strong Action Verbs
                  </span>

                  <strong>
                    {result
                      ?.step_35_bullet_analysis
                      ?.action_verb_bullets ??
                      "N/A"}
                  </strong>

                </div>

              </div>

            </div>

            {/* ACHIEVEMENT ANALYSIS */}

            <div className="dashboard-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    ACHIEVEMENT ANALYSIS
                  </p>

                  <h2>
                    Achievement & Quantification
                  </h2>
                </div>

              </div>

              <div className="achievement-card">

                <div className="achievement-status">

                  {result
                    ?.step_36_achievement_analysis
                    ?.status ||
                    "Limited Quantified Achievements"}

                </div>

                <p>
                  Quantified achievements:{" "}
                  {result
                    ?.step_36_achievement_analysis
                    ?.quantified_count ??
                    0}
                </p>

                <p>
                  Achievement statements:{" "}
                  {result
                    ?.step_36_achievement_analysis
                    ?.achievement_count ??
                    0}
                </p>

              </div>

            </div>

            {/* FINAL SUMMARY */}

            <div className="dashboard-card final-summary-card">

              <div className="dashboard-card-header">

                <div>
                  <p className="eyebrow">
                    FINAL SUMMARY
                  </p>

                  <h2>
                    Resume Analysis Summary
                  </h2>
                </div>

              </div>

              <div className="final-summary">

                <div className="summary-status">

                  {result
                    ?.step_40_analysis_summary
                    ?.resume_status ||
                    "Analysis Complete"}

                </div>

                <p>
                  {result
                    ?.step_40_analysis_summary
                    ?.summary ||
                    "Resume analysis completed successfully."}
                </p>

              </div>

            </div>

            {/* JSON DETAILS */}

            <details className="json-details">

              <summary>
                View Complete Analysis JSON
              </summary>

              <pre>
                {JSON.stringify(
                  result,
                  null,
                  2
                )}
              </pre>

            </details>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;