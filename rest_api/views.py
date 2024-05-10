from rest_framework.response import Response

from rest_api.models import Flat

from rest_framework.views import APIView
from django.db.models import Avg, Min, Max, Sum


class FlatAPIInfo(APIView):
    def get(self, request):
        info = {
            'flats count': Flat.objects.count(),
            'flats avg monthly price': round(Flat.objects.aggregate(Avg('price_per_month'))['price_per_month__avg'], 2),
            'flats min monthly price': round(Flat.objects.aggregate(Min('price_per_month'))['price_per_month__min'], 2),
            'flats max monthly price': round(Flat.objects.aggregate(Max('price_per_month'))['price_per_month__max'], 2)
        }
        return Response(info, status=200)



# class FlatAPIInfo(APIView):
#     def get(self, request):

class FlatAPIView(APIView):
    def get(self, request):
        queryset = Flat.objects.all().values()
        params = request.query_params
        price_per_m2_coeff_user = 3
        common_ecology_coeff_user = 3
        population_density_coeff_user = 3
        green_spaces_coeff_user = 3
        negative_impact_coeff_user = 3
        phone_nets_coeff_user = 3
        crime_coeff_user = 3
        try:
            for param in params:
                if param == "min_price":
                    queryset = queryset.filter(price_per_month__gte=params[param])
                elif param == "max_price":
                    queryset = queryset.filter(price_per_month__lte=params[param])
                elif param == "rooms":
                    queryset = queryset.filter(rooms=params[param])
                elif param == "region":
                    queryset = queryset.filter(region=params[param])
                elif param == "district":
                    queryset = queryset.filter(district=params[param])
                elif param == "underground":
                    queryset = queryset.filter(underground=params[param])
                elif param == "price_per_m2_coeff":
                    price_per_m2_coeff_user = int(params[param])
                elif param == "common_ecology_coeff":
                    common_ecology_coeff_user = int(params[param])
                elif param == "population_density_coeff":
                    population_density_coeff_user = int(params[param])
                elif param == "green_spaces_coeff":
                    green_spaces_coeff_user = int(params[param])
                elif param == "negative_impact_coeff":
                    negative_impact_coeff_user = int(params[param])
                elif param == "phone_nets_coeff":
                    phone_nets_coeff_user = int(params[param])
                elif param == "crime_coeff":
                    crime_coeff_user = int(params[param])
                else:
                    return Response("Wrong parameters", status=400)
        except(ValueError):
            return Response("Wrong parameter value", status=400)
        if(queryset.count() == 0):
            return Response("No flats fount", status=200)
        min_price = queryset.aggregate(Min('price_per_m2'))['price_per_m2__min']
        max_price = queryset.aggregate(Max('price_per_m2'))['price_per_m2__max']
        difference = max_price - min_price
        flatlist = list(queryset)
        for flat in flatlist:
            price_per_m2_score = (10. - round((flat['price_per_m2'] - min_price)/(0.0000001 + difference / 10.), 2)) * price_per_m2_coeff_user
            flat["price_per_m2_score"] = price_per_m2_score
            common_ecology_score = round(flat['common_ecology_coeff'] * common_ecology_coeff_user, 2)
            flat["common_ecology_score"] = common_ecology_score
            population_density_score = round(flat['population_density_coeff'] * population_density_coeff_user, 2)
            flat["population_density_score"] = population_density_score
            green_spaces_score = round(flat['green_spaces_coeff'] * green_spaces_coeff_user, 2)
            flat["green_spaces_score"] = green_spaces_score
            negative_impact_score = round(flat['negative_impact_coeff'] * negative_impact_coeff_user, 2)
            flat["negative_impact_score"] = negative_impact_score
            phone_nets_score = round(flat['phone_nets_coeff'] * phone_nets_coeff_user, 2)
            flat["phone_nets_score"] = phone_nets_score
            crime_score = round(flat['crime_coeff'] * crime_coeff_user, 2)
            flat["crime_score"] = crime_score
            flat['score'] = round(price_per_m2_score + common_ecology_score + population_density_score + green_spaces_score + negative_impact_score + phone_nets_score + crime_score, 2)
        flatlist.sort(key=lambda flat: flat["score"], reverse=True)
        return Response(flatlist)

