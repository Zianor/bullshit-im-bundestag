import data_preparation
import data_visualization

if __name__ == "__main__":
    comment_list = data_preparation.load_data(False)
    save = True

    dict_direct = data_preparation.get_data_matrix_direct_calls(comment_list, relative=True)
    data_visualization.create_heatmap(dict_direct, 'Verhältnis von direkten Zurufen zu Parteigröße', relative=True)
    
    dict_direct_total = data_preparation.get_data_matrix_direct_calls(comment_list, relative=False)
    data_visualization.create_heatmap(dict_direct_total, 'absolute Anzahl an direkten Zurufen')
    
    dict_laughter = data_preparation.get_data_matrix_laughter(comment_list, relative=True, weighted=True)
    data_visualization.create_heatmap(dict_laughter, 'Verhältnis von Lachen zu Parteigröße', relative=True)

    dict_laughter_total = data_preparation.get_data_matrix_laughter(comment_list, relative=False, weighted=True)
    data_visualization.create_heatmap(dict_laughter_total, 'absolute Anzahl an Lachen')

    dict_applause = data_preparation.get_data_matrix_applause(comment_list, relative=True, weighted=True)
    data_visualization.create_heatmap(dict_applause, 'Verhältnis Beifall zu Parteigröße', relative=True)

    dict_applause_total = data_preparation.get_data_matrix_applause(comment_list, relative=False, weighted=True)
    data_visualization.create_heatmap(dict_applause_total, 'absolute Anzahl an Beifall')

    dict_applause_self = data_preparation.create_distribution_self_other(dict_applause)
    data_visualization.visualize_distribution_self_other(dict_applause_self, 'Beifall für die eigene Partei in %')

    dict_comments = data_preparation.get_data_matrix_comments(comment_list, relative=True, weighted=True)
    data_visualization.create_heatmap(dict_comments, 'Verhältnis Kommentarzahl zu Parteigröße', relative=True)

    dict_comments_total = data_preparation.get_data_matrix_comments(comment_list, relative=False, weighted=True)
    data_visualization.create_heatmap(dict_comments_total, 'absolute Anzahl an Kommentaren')

    dict_comment_self = data_preparation.create_distribution_self_other(dict_comments)
    data_visualization.visualize_distribution_self_other(dict_comment_self, 'Kommentare zur eigenen Partei in %')

    if save:
        data_visualization.create_heatmap(dict_direct, 'Verhältnis direkten Zurufen zu Parteigröße',
                                          'graphics/direct_comments_relative.png', relative=True)
        data_visualization.create_heatmap(dict_direct_total, 'absolute Anzahl an direkten Zurufen',
                                          'graphics/direct_comments_absolute.png')
        data_visualization.create_heatmap(dict_laughter, 'Verhältnis von Lachen zu Parteigröße (gewichtet)',
                                          'graphics/laughter_relative.png', relative=True)
        data_visualization.create_heatmap(dict_laughter_total, 'absolute Anzahl an Lachen (gewichtet)',
                                          'graphics/laughter_absolute.png')
        data_visualization.visualize_distribution_self_other(dict_applause_self, 'Beifall für die eigene Partei in %',
                                                             'graphics/applause_self.png')
        data_visualization.create_heatmap(dict_comments, 'Verhältnis Kommentarzahl zu Parteigröße (gewichtet)',
                                          'graphics/comments_relative.png', relative=True)
        data_visualization.create_heatmap(dict_comments_total, 'absolute Anzahl an Kommentaren (gewichtet)',
                                          'graphics/comments_absolute.png')
        data_visualization.visualize_distribution_self_other(dict_comment_self, 'Kommentare zur eigenen Partei in %',
                                                             'graphics/comments_self.png')
        data_visualization.create_heatmap(dict_applause_total, 'absolute Anzahl an Beifall (gewichtet)',
                                          'graphics/applause_absolute.png')
        data_visualization.create_heatmap(dict_applause, 'Verhältnis Beifall zu Parteigröße (gewichtet)',
                                          'graphics/applause_relative.png', relative=True)
