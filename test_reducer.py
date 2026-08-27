from reducer import reduce_summaries


summaries = [
    """
    - The speaker explains that fake internships often charge students money.
    - Legitimate internships should provide real work and supervision.
    """,

    """
    - Students are increasingly pressured to obtain internships for placement.
    - Some companies exploit this pressure by selling training programs as internships.
    """,

    """
    - Candidates should avoid paying for internship opportunities.
    - Building independent projects and applying to smaller startups can provide real experience.
    """,
]


if __name__ == "__main__":
    result = reduce_summaries(summaries)

    print("\nREDUCER TEST")
    print("=" * 60)
    print(result)