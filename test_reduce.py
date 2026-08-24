from reducer import reduce_summaries


fake_summaries = [
    """
- The speaker investigates fake internships targeting freshers.
- A suspicious listing advertised removing the fresher tag.
- The internship had vague duration and unpaid compensation.
""",
    """
- The application required basic details and immediately added applicants
  to a WhatsApp group.
- The organizers presented training, certificates, and resume assistance.
- Participants were eventually asked for money.
""",
    """
- The speaker argues that paid training programs should not be presented
  as genuine internships.
- Students should build independent projects instead.
- Genuine internships should involve real clients and real work.
""",
]


result = reduce_summaries(fake_summaries)

print("\nFINAL SUMMARY")
print("=" * 60)
print(result)