export type DefinitionEntry = [term: string, description: string];

interface DefinitionListProps {
  className: string;
  entries: DefinitionEntry[];
}

export default function DefinitionList({ className, entries }: DefinitionListProps) {
  return (
    <dl className={className}>
      {entries.map(([term, description], index) => (
        <div key={`${term}-${index}`}>
          <dt>{term}</dt>
          <dd>{description}</dd>
        </div>
      ))}
    </dl>
  );
}
