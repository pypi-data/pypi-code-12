#!/usr/bin/python
# -*- coding: utf-8 -*-
def filter_by_dict(query_set, filter_dict={}, exclude_dict={}, ordering_list=[]):
	''':param pk int: Primary key do delivery basket:
	   :param query_set QuerySet : Query set sobre o qual devem ser aplicados os filtros :
		 :param filter_list list   : lista de dicionários para filter com keys 'field' (campo do modelo já incluindo o relation ex: id__in),'value' (valor do filtro) :
		 :param exclude_list list  : lista de dicionários para exclude com keys 'field' (campo do modelo já incluindo o relation ex: id__in), 'value' (valor do filtro) 
		 :param ordering_list list : lista de string para ser passada para a função order_by :
		 Filtra o queryset usando filter_list como argumentos da função filter, exclude_list para a função exclude e ordering_list para order by
	'''
	return query_set.filter(**filter_dict).exclude(**exclude_dict).order_by(*ordering_list)
