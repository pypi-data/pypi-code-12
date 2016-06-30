import error as e
import plotting as p

x = e.Measurement([1, 2, 3, 4, 5], [0.5], name='Length', units='cm')
y = e.Measurement([5, 7, 11, 14, 17], [1], name='Mass', units='g')

figure = p.Plot(x, y)
figure.fit('linear')
figure.residuals()
intercept1, slope1 = figure.fit_parameters

x2 = e.Measurement([1, 2, 3, 4, 5], [0.5], name='Length', units='cm')
y2 = e.Measurement([6, 8, 12, 15, 18], [1], name='Mass', units='g')

figure2 = p.Plot(x2, y2)
figure2.fit('linear')
figure2.residuals()
intercept2, slope2 = figure2.fit_parameters


def theoretical(x):
    return 3 + 2*x

figure.show_on(figure2, 'file')
