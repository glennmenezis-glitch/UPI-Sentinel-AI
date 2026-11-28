
import networkx as nx


def analyze_network(connection):

    graph = nx.DiGraph()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT sender_id, receiver_id, amount
        FROM transactions
    """)

    transactions = cursor.fetchall()

    for transaction in transactions:
        sender = transaction["sender_id"]
        receiver = transaction["receiver_id"]
        amount = transaction["amount"]

        graph.add_edge(
            sender,
            receiver,
            amount=amount
        )

    # Find accounts receiving money from multiple accounts
    suspicious_accounts = []

    for account in graph.nodes():
        incoming = graph.in_degree(account)

        if incoming >= 3:
            suspicious_accounts.append({
                "account": account,
                "incoming_connections": incoming,
                "reason": "Multiple incoming transaction sources"
            })

    # Find circular transaction patterns
    suspicious_cycles = list(
        nx.simple_cycles(graph)
    )

    return {
        "total_accounts": graph.number_of_nodes(),
        "total_connections": graph.number_of_edges(),
        "suspicious_accounts": suspicious_accounts,
        "suspicious_cycles": suspicious_cycles
    }
