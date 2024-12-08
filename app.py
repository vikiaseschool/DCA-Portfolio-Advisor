from flask import Flask, render_template, request, redirect, url_for, flash
import yfinance as yf
import finance  # Tento modul předpokládáme pro získání ročního výnosu a rizika.

app = Flask(__name__)
app.secret_key = 'your-secret-key'
# Definice mapy instrumentů
instrument_map = {
    'VOO': ('S&P 500 ETF', 10, 'Medium Risk'),
    'URTH': ('iShares MSCI World ETF', 7.5, 'Medium Risk'),
    'QQQ': ('Nasdaq 100 ETF', 12, 'High Risk'),
    'VNQ': ('Real Estate ETF', 9, 'Medium Risk'),
    'BND': ('Total Bond Market ETF', 3, 'Low Risk'),
    'GLD': ('Gold', 5, 'Medium Risk'),
    'BTC': ('Bitcoin', 30, 'High Risk')
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        instrument = request.form['instrument']
        custom_ticker = request.form.get('custom_ticker')
        horizon = request.form['horizon']
        start_capital = request.form['start_capital']
        frequency = request.form['frequency']
        how_much = request.form['how_much']

        if instrument != 'None':
            ticker = instrument
        elif custom_ticker:
            try:
                stock = yf.Ticker(custom_ticker)
                history = stock.history(period="1d")
                if history.empty:
                    raise ValueError("No data found for the ticker.")
                ticker = custom_ticker
            except Exception:
                flash(f"Invalid Ticker '{custom_ticker}', please try again.", "error")
                return redirect(url_for('index'))
        else:
            flash("Please select an instrument or enter a custom ticker.", "error")
            return redirect(url_for('index'))

        if ticker in instrument_map.keys():
            annual_return = instrument_map[ticker][1]
            risk = instrument_map[ticker][2]
        else:
            annual_return = finance.get_annual_return_since_listing(ticker)
            if annual_return < 5:
                risk = 'Medium Risk'
            else:
                risk = 'High Risk'

        if ticker != 'BTC':
            instrument_name = finance.get_company_name(ticker)
        else:
            instrument_name = 'Bitcoin'

        total_assets = finance.calculate_total_assets(float(start_capital), annual_return, float(horizon),
                                                      int(frequency), float(how_much))
        total_profit, total_profit_perc = finance.get_total_profit(float(start_capital), float(how_much), int(frequency),
                                                int(horizon), total_assets)
        investment_values = finance.get_values_for_graph(float(start_capital), annual_return, float(horizon), float(how_much), int(frequency))
        # Přesměrování na stránku s výsledky s hodnotami v URL parametrech
        return render_template('result.html', instrument=instrument_name,
                               horizon=horizon, ticker=ticker, risk=risk, annual_return=annual_return,
                               start_capital=start_capital, frequency=frequency, how_much=how_much,
                               total_assets=total_assets, total_profit=total_profit, total_profit_perc=total_profit_perc, investment_values=investment_values)

    return render_template('index.html')


# Route pro zobrazení výsledků
@app.route('/result', methods=['GET'])
def result():
    # Načítání hodnot z URL (GET parameters)
    ticker = request.args.get('ticker')
    instrument_name = request.args.get('instrument')
    risk = request.args.get('risk')
    total_profit = request.args.get('total_profit')
    investment_values = request.args.get('investment_values')
    total_profit_perc = request.args.get('total_profit_perc')
    total_assets = request.args.get('total_assets')
    annual_return = request.args.get('annual_return')
    horizon = request.args.get('horizon')
    start_capital = request.args.get('start_capital')
    frequency = request.args.get('frequency')
    how_much = request.args.get('how_much')

    return render_template('result.html', instrument=instrument_name,
                           ticker=ticker, horizon=horizon,
                           start_capital=start_capital,
                           frequency=frequency, how_much=how_much,
                           risk=risk, annual_return=annual_return, total_assets=total_assets, total_profit=total_profit, total_profit_perc=total_profit_perc,
                           investment_values=investment_values)


if __name__ == '__main__':
    app.run(debug=True)
