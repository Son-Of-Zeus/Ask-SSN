import { FileText, ChevronRight } from 'lucide-react';
const CitationItem = ({ citation, index }) => {
  const pageInfo = citation.page_number && citation.page_number !== 'Unknown Page'
    ? ` (Page: ${citation.page_number})`
    : '';

  return (
    <li className="citation-item">
      <details>
        <summary className="citation-item-header">
          <FileText size={16} className="citation-icon" />
          <span className="citation-text">
            {index + 1}. {citation.document_name || 'Unknown Source'}{pageInfo}
          </span>
        </summary>
        <div className="citation-content-preview">
          {citation.content
            ? <p>"{citation.content}"</p>
            : <p className="no-preview">No content preview available.</p>
          }
        </div>
      </details>
    </li>
  );
};

const Citations = ({ citations }) => {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className="citations-container">
      <details>
        <summary className="sources-header">
          <ChevronRight className="chevron-icon" size={20} />
          <span className="sources-title">
            Sources ({citations.length})
          </span>
        </summary>
        <ul className="citations-list">
          {citations.map((citation, index) => (
            <CitationItem
              key={index}
              citation={citation}
              index={index}
            />
          ))}
        </ul>
      </details>
    </div>
  );
};

export default Citations;
