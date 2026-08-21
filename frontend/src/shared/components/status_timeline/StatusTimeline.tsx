export interface TimelineEntry {
  new_status: string;
  previous_status: string | null;
  timestamp: string;
  reason: string | null;
  next_action: string | null;
}

interface StatusTimelineProps {
  entries: TimelineEntry[];
}

// Role-appropriate status timeline component shared across workspaces
// (T154, User Story 6, FR-025). The server already applies role-based
// filtering (status_timeline_service); this component just renders whatever
// it receives.
export function StatusTimeline({ entries }: StatusTimelineProps) {
  if (entries.length === 0) {
    return <p>No status history is available yet.</p>;
  }

  return (
    <ol aria-label="Case status timeline">
      {entries.map((entry, index) => (
        <li key={`${entry.new_status}-${entry.timestamp}-${index}`}>
          <p>
            <strong>{entry.new_status.replace(/_/g, " ")}</strong>{" "}
            <time dateTime={entry.timestamp}>{new Date(entry.timestamp).toLocaleString()}</time>
          </p>
          {entry.reason && <p>Reason: {entry.reason}</p>}
          {entry.next_action && <p>Next: {entry.next_action}</p>}
        </li>
      ))}
    </ol>
  );
}
