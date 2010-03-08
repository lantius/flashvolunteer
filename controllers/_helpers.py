import random

from models.interestcategory import InterestCategory


class NeighborhoodHelper():
    def selected(self, application, selected_neighborhood):
        neighborhoods = []
        for neighborhood in application.neighborhoods.order('name').fetch(limit=500):
            if selected_neighborhood:
                if neighborhood.key().id() == selected_neighborhood.key().id():
                    neighborhood.selected = True
            neighborhoods.append(neighborhood)
        return neighborhoods

#TODO: convert interest category helper to application-specific data model
class InterestCategoryHelper():
    def selected(self, selector):
        interestcategories = []
        for interestcategory in InterestCategory.all().order('name').fetch(limit=500):
            for sic in selector.interestcategories():
                if sic.key().id() == interestcategory.key().id():
                    interestcategory.selected = True
            interestcategories.append(interestcategory)
        return interestcategories
