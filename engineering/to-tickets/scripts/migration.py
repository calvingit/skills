"""Explicit, transactional v1 -> v2 field migration. Never rebind authority."""
from ticket_graph.contracts import envelope, problem, validate_ticket
from ticket_graph.graph import public_ticket
from ticket_graph.store import acquire_write_lock, release_lock, read_raw_tickets, commit_graph_transaction


def migrate(task_dir):
    descriptor, _, problems = acquire_write_lock(task_dir)
    if problems:
        return envelope('migrate', ok=False, problems=problems), 1
    try:
        tickets, problems = read_raw_tickets(task_dir)
        changed = []
        for ticket in tickets:
            if isinstance(ticket.get('lifecycle'), dict) and ticket['lifecycle'].get('phase') == 'in_progress':
                problems.append(problem('transition', 'active_attempts', 'Stop writers and block active attempts with the previous version before migration.'))
            if ticket.get('schema_version') == 1:
                for old, new in [('design_decisions', 'referenced_design_decisions'), ('acceptance_criteria', 'delivery_acceptance')]:
                    if old not in ticket or new in ticket:
                        problems.append(problem('contract', 'ambiguous_migration', f'Expected only legacy field {old}.'))
                    else:
                        ticket[new] = ticket.pop(old)
                ticket['schema_version'] = 2
                changed.append(ticket['id'])
            problems.extend(validate_ticket(public_ticket(ticket), ticket['_path']))
        if not problems and changed:
            problems = commit_graph_transaction(task_dir, tickets, 'migrate-v2')
        return envelope('migrate', ok=not problems, result={'migrated': changed if not problems else []}, problems=problems), int(bool(problems))
    finally:
        release_lock(descriptor)
