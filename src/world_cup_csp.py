import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        # Las variables son los equipos.
        self.variables = list(teams.keys())

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """
        FIFA = assignment.items()
        
        count = sum(1 for t, g in FIFA if g == group)

        # Implementado: implementar restricción de tamaño del grupo (máximo 4)
        if count >= 4:
            if self.debug:
                print(f"Restricción de tamaño del grupo violada: {group} ya tiene 4 equipos.")
            return False
        

        group_assigned = [t for t, g in FIFA if g == group]

        for assigned_team in group_assigned:
            if self.get_team_pot(assigned_team) == self.get_team_pot(team):
                if self.debug:
                    print(f"Restricción de bombo violada: {team} y {assigned_team} están en el mismo bombo.")
                return False
            else:
                if self.get_team_confederation(assigned_team) == self.get_team_confederation(team):
                    if self.get_team_confederation(team) == "UEFA":
                        #para cada equipo de la UEFA solo se permiten dos equipos en el mismo grupo
                        count_uefa = sum(1 for t in group_assigned if self.get_team_confederation(t) == "UEFA")
                        if count_uefa >= 2:
                            if self.debug:
                                print(f"Restricción de confederación violada: {group} ya tiene 2 equipos de UEFA.")
                            return False
                    else:
                        if self.debug:
                            print(f"Restricción de confederación violada: {team} y {assigned_team} son de la misma confederación.")
                        return False


        return True

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Debe eliminar valores inconsistentes en dominios futuros.
        Retorna True si la propagación es exitosa, False si algún dominio queda vacío.
        """
        # Hacemos una copia de los dominios actuales para modificarla de forma segura
        new_domains = copy.deepcopy(domains)

        for team in self.variables:
            if team not in assignment:
                #Para los equipos no asignados, filtramos sus dominios
                #segun la asignacion actual
                valid_groups = []
                for group in new_domains[team]:
                    if self.is_valid_assignment(group, team, assignment):
                        valid_groups.append(group)

                new_domains[team] = valid_groups
                if not valid_groups:
                    if self.debug:
                        print(f"Dominio vacío para {team} después de forward checking.")
                    return False, new_domains
                
        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """
        # TODO: implementar MRV
        # Este es un valor de retorno por defecto, debes modificarlo
        #listado de equipos no asignados
        unassigned_vars = [v for v in self.variables if v not in assignment]

        min_count = 999999
        team_min = None

        for team in unassigned_vars:
            if len(domains[team]) < min_count:
                min_count = len(domains[team])
                team_min = team
        

        return team_min if unassigned_vars else None

    def backtrack(self, assignment, domains=None):
        if domains is None:
            domains = copy.deepcopy(self.domains)
        if len(assignment) == len(self.variables):
            return assignment

        var_team = self.select_unassigned_variable(assignment, domains)
        for group in domains[var_team]:
            if self.is_valid_assignment(group, var_team, assignment):
                new_assignment = copy.deepcopy(assignment)
                new_assignment[var_team] = group
                success, new_domains = self.forward_check(new_assignment, domains)
                if success:
                    result = self.backtrack(new_assignment, new_domains)
                    if result is not None:
                        return result
        return None
