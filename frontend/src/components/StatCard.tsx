export default function StatCard({
  label,
  value,
  tone = "blue",
}: {
  label: string;
  value: number;
  tone?: "blue" | "amber" | "teal";
}) {
  return (
    <article className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
