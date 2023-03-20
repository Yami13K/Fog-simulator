from LoadBalancingAgorithms.Reinforcement_Learning.Sorting_methods import NonDominatingSorting, TLO


class Sort:
    def __init__(self):
        self.NDS_sorting_algorithm = NonDominatingSorting.NonDominatingSorting()
        self.TLO_sorting_algorithm = TLO.TLO()

    def __call__(self, sort_type, data):
        if sort_type == 'NDS':
            return self.NDS_sorting_algorithm.non_dominating_sort(data)
        elif sort_type == 'TLO':
            return self.TLO_sorting_algorithm.threshold_lexicographical_sort(data)
        else:
            raise ValueError('No such algorithm')
