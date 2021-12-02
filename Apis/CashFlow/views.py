from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from keras.models import load_model
import numpy as np
from rest_framework.response import Response
from sklearn.preprocessing import StandardScaler
from django.contrib.staticfiles.finders import find


# Create your views here.
@csrf_exempt
def homepage(request):
    if request.method == 'POST':
        bedrooms = request.POST.get('bedrooms')  # @param {type:"number"}
        bathrooms = request.POST.get('bathrooms')  # @param {type:"number"}
        square_feet = request.POST.get('square_feet')  # @param {type:"number"}
        condition = request.POST.get('condition')  # @param {type:"slider", min:1, max:5, step:1}
        zipcode = request.POST.get('zipcode')  # @param {type:"number"}
        duration = int(request.POST.get('duration', 10))  # @param {type:"number"} time for which we have to calculte
        principle = int(request.POST.get('mortgage_principle'))
        roi = int(request.POST.get('roi', 0))
        time = int(request.POST.get('time', 0))# loan duration

        url = find('house_price.h5')
        model = load_model(url)
        s_scaler = StandardScaler()
        input = np.array([bedrooms, bathrooms, square_feet, condition, zipcode])
        input = input.reshape((1, -1))
        input = s_scaler.fit_transform(input.astype(np.float))
        price = int(model.predict(input)[0][0])
        print(price)
        url = find('house_rent.h5')
        model = load_model(url)
        s_scaler = StandardScaler()
        input = np.array([bedrooms, bathrooms, square_feet, condition, zipcode])
        input = input.reshape((1, -1))
        input = s_scaler.fit_transform(input.astype(np.float))
        rent = model.predict(input)[0][0]

        url = find('house_tax.h5')
        model = load_model(url)
        s_scaler = StandardScaler()
        input = np.array([bedrooms, bathrooms, square_feet, condition, zipcode])
        input = input.reshape((1, -1))
        input = s_scaler.fit_transform(input.astype(np.float))

        house_tax = model.predict(input)[0][0]
        total_amount = int(price)
        if principle:
            print(price, principle)
            loan_amount = price - principle
            amount = principle * (pow((1 + roi / 100), time))
            total_amount = loan_amount + amount

        profit = duration * rent * 12 - total_amount - house_tax * duration * 12

        if profit >= 0:
            return render(request, 'LandingPage.html',
                          {'result': 'Your net Profit' ' in this investment will be $  {pf}'.format(pf=profit)})
        else:
            profit = (-1) * profit
            return render(request, 'LandingPage.html',
                          {'result': 'Your net Loss' ' in this investment will be $  {pf}'.format(pf=profit)})

    return render(request, 'LandingPage.html', {'result': None})
