#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal, sys, sistea, bladeRF_transceiver, datetime
from gnuradio import gr
from time import sleep
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qwt5.Qwt import QwtThermo
#!/usr/bin/python
import signal
import sys
from gnuradio import gr
import bladeRF_transceiver
from time import sleep
import datetime



class SisTeA_App(QtGui.QMainWindow, sistea.Ui_MainWindow, QtGui.QDialog, bladeRF_transceiver.bladeRF_transceiver):

    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        self.flag = 0
        self.mod = 0

        self.tx_freq.setMaximum(1000)
        self.rx_freq.setMaximum(1000)

        self.tx_freq.setProperty("value", 902)
        self.rx_freq.setProperty("value", 900)
       
        self.tx_freq_value.setText(str(self.tx_freq.value()))
        self.tx_rf_gain_value.setText(str(self.tx_rf_gain.value()))
        self.tx_bb_gain_value.setText(str(self.tx_bb_gain.value()))
        self.rx_freq_value.setText(str(self.rx_freq.value()))
        self.rx_rf_gain_value.setText(str(self.rx_rf_gain.value()))
        self.rx_bb_gain_value.setText(str(self.rx_bb_gain.value()))
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.recv_frame)
        self.timer.start(10)

        self.timer1 = QtCore.QTimer(self)
        self.timer1.timeout.connect(self.send_beacon)

        self.gmsk_radioButton.released.connect(self.modulation_selection)
        self.gfsk_radioButton.released.connect(self.modulation_selection)

        self.bandwith_line.returnPressed.connect(self.set_bandwith)
        self.samp_rate_line.returnPressed.connect(self.set_samp_rate)
        self.symbol_rate_line.returnPressed.connect(self.set_symbol_rate)
        
        self.tx_freq_value.returnPressed.connect(self.set_tx_freq_value)
        self.tx_bb_gain_value.returnPressed.connect(self.set_tx_bb_gain_value)
        self.tx_rf_gain_value.returnPressed.connect(self.set_tx_rf_gain_value)

        self.rx_freq_value.returnPressed.connect(self.set_rx_freq_value)
        self.rx_bb_gain_value.returnPressed.connect(self.set_rx_bb_gain_value)
        self.rx_rf_gain_value.returnPressed.connect(self.set_rx_rf_gain_value)

        self.btn_send.released.connect(self.start_tx)
        self.tx_freq.valueChanged.connect(self.set_tx_freq)
        self.tx_rf_gain.valueChanged.connect(self.set_tx_rf_gain)
        self.tx_bb_gain.valueChanged.connect(self.set_tx_bb_gain)
        self.rx_freq.valueChanged.connect(self.set_rx_freq)
        self.rx_rf_gain.valueChanged.connect(self.set_rx_rf_gain)
        self.rx_bb_gain.valueChanged.connect(self.set_rx_bb_gain)
        
        self.rf = bladeRF_transceiver.bladeRF_transceiver()
        self.rf.set_frequency_tx(long(self.tx_freq.value())*1e6)
        self.rf.set_frequency_rx(long(self.rx_freq.value())*1e6)

        self.rf.set_tx_rf_gain(self.tx_rf_gain.value())
        self.rf.set_tx_bb_gain(self.tx_bb_gain.value())         # [-35,-4]
        self.rf.set_rx_rf_gain(self.rx_rf_gain.value())           # {0, 3, 6}
        self.rf.set_rx_bb_gain(self.rx_bb_gain.value())          # [5,60]
        self.bandwith_line.setText(str(self.rf.get_bandwith()))
        self.samp_rate_line.setText(str(self.rf.get_samp_rate()))
        self.sps_line.setText(str(self.rf.get_samp_per_sym()))
        self.symbol_rate_line.setText(str(self.rf.get_symbole_rate()))

        self.rf.set_mod_selector(0)
        self.rf.set_demod_selector(0)
        self.rf.set_tx_valve_gmsk_value(False) 
        self.rf.set_tx_valve_gfsk_value(True) 
        self.rf.set_rx_valve_gmsk_value(False) 
        self.rf.set_rx_valve_gfsk_value(True) 


    def set_bandwith(self):
        print self.rf.set_bandwith(float(self.bandwith_line.text()))
    def set_samp_rate(self):
        print self.rf.set_samp_rate(float(self.samp_rate_line.text()))

    def set_symbol_rate(self):
        self.rf.set_symbole_rate(float(self.symbol_rate_line.text()))
        self.sps_line.setText(str(self.rf.get_samp_per_sym()))
        
    def set_tx_freq_value(self):
        self.rf.set_frequency_tx(long(float(self.tx_freq_value.text())*1e6))        
        self.tx_freq.setProperty("value", float(self.tx_freq_value.text()))
        print "Tx Frequency = "+ str(self.rf.get_frequency_tx()) + "Hz"
    def set_tx_rf_gain_value(self):
        self.rf.set_tx_rf_gain(long(float(self.tx_rf_gain_value.text())))        
        self.tx_rf_gain.setProperty("value", float(self.tx_rf_gain_value.text()))
        print "Tx rf gain = "+ str(self.rf.get_tx_rf_gain()) + "dB"
    def set_tx_bb_gain_value(self):
        self.rf.set_tx_bb_gain(long(float(self.tx_bb_gain_value.text())))        
        self.tx_bb_gain.setProperty("value", float(self.tx_bb_gain_value.text()))
        print "Tx bb gain = "+ str(self.rf.get_tx_bb_gain()) + "dB"

    def set_rx_freq_value(self):
        self.rf.set_frequency_rx(long(float(self.rx_freq_value.text())*1e6))        
        self.rx_freq.setProperty("value", float(self.rx_freq_value.text()))
        print "Rx Frequency = "+ str(self.rf.get_frequency_rx()) + "Hz"
    def set_rx_rf_gain_value(self):
        self.rf.set_rx_rf_gain(long(float(self.rx_rf_gain_value.text())))        
        self.rx_rf_gain.setProperty("value", float(self.rx_rf_gain_value.text()))
        print "Rx rf gain = "+ str(self.rf.get_rx_rf_gain()) + "dB"
    def set_rx_bb_gain_value(self):
        self.rf.set_rx_bb_gain(long(float(self.rx_bb_gain_value.text())))        
        self.rx_bb_gain.setProperty("value", float(self.rx_bb_gain_value.text()))
        print "Rx bb gain = "+ str(self.rf.get_rx_bb_gain()) + "dB"

    def set_tx_freq_value(self):
        self.rf.set_frequency_tx(long(float(self.tx_freq_value.text())*1e6))        
        self.tx_freq.setProperty("value", float(self.tx_freq_value.text()))
        print "Tx Frequency = "+ str(self.rf.get_frequency_tx()) + "Hz"

    def set_tx_freq(self):
        self.rf.set_frequency_tx(long(self.tx_freq.value()*1e6))          
        self.tx_freq_value.setText(str(self.tx_freq.value()))
        print "Tx Frequency = "+ str(self.rf.get_frequency_tx()) + "Hz"
    def set_tx_rf_gain(self):
        self.rf.set_tx_rf_gain(self.tx_rf_gain.value())          # [0,25]
        self.tx_rf_gain_value.setText(str(self.tx_rf_gain.value()))
    def set_tx_bb_gain(self):
        self.rf.set_tx_bb_gain(self.tx_bb_gain.value())          # [-35,-4]
        self.tx_bb_gain_value.setText(str(self.tx_bb_gain.value()))

    def set_rx_freq(self):
        self.rf.set_frequency_rx(long(self.rx_freq.value()*1e6))          # [0,25]
        self.rx_freq_value.setText(str(self.rx_freq.value()))
    def set_rx_rf_gain(self):
        self.rf.set_rx_rf_gain(self.rx_rf_gain.value())          # {0, 3, 6}
        self.rx_rf_gain_value.setText(str(self.rx_rf_gain.value()))
    def set_rx_bb_gain(self):
        self.rf.set_rx_bb_gain(self.rx_bb_gain.value())          # [5,60]
        self.rx_bb_gain_value.setText(str(self.rx_bb_gain.value()))

    def modulation_selection(self):
        if self.gfsk_radioButton.isChecked() == True:
            print "Modulation Selected = GFSK"
            self.rf.set_mod_selector(1)
            self.rf.set_demod_selector(1)
            self.rf.set_tx_valve_gmsk_value(True) 
            self.rf.set_tx_valve_gfsk_value(False) 
            self.rf.set_rx_valve_gmsk_value(True) 
            self.rf.set_rx_valve_gfsk_value(False) 
        elif self.gmsk_radioButton.isChecked() == True:
            print "Modulation Selected = GMSK"
            self.rf.set_mod_selector(0)
            self.rf.set_demod_selector(0)
            self.rf.set_tx_valve_gmsk_value(False) 
            self.rf.set_tx_valve_gfsk_value(True) 
            self.rf.set_rx_valve_gmsk_value(False) 
            self.rf.set_rx_valve_gfsk_value(True) 
        
    def start_tx(self):
        if self.flag == 0:
            self.rf.start()
            self.send_beacon()
            self.btn_send.setText("STOP")
            self.timer1.start(6000)
            self.flag = 1
            
        elif self.flag == 1:
            self.btn_send.setText("START")
            self.rf.stop()
            self.rf.wait()
            self.timer1.stop()
            self.flag = 0
            

    def send_str(self, payload):
        self.rf.msg_source_msgq_in.insert_tail(gr.message_from_string(payload))
   
    def recv_str(self):
        self.pkt = self.rf.msg_sink_msgq_out.delete_head_nowait().to_string()
        return self.pkt

    def recv_frame(self):
        if self.rf.msg_sink_msgq_out.empty_p()==False:
            self.msg = self.recv_str()
            self.rssi_value = str(self.rf.probe_signal_1.level())
            print self.msg + "," + self.rssi_value
            self.sensor_1.setProperty("value", float(self.msg[32:37]))
            self.lcdNumber_1.setProperty("value", float(self.msg[32:37]))
            self.sensor_2.setProperty("value", float(self.msg[40:45]))
            self.lcdNumber_2.setProperty("value", float(self.msg[40:45]))
            sleep(1)
            self.rf.msg_sink_msgq_out.flush()
   
    def send_beacon(self):
        for x in range(0, 10):
            self.send_str('A101')


    def about(self):
        ##QtGui.QMessageBox.about(self, "About Ground Plane Antenna Calculator", "about message: <br />hello PyQt/PySide")
        QtGui.QMessageBox.about(self, "About Ground Plane Antenna Calculator", "<b>Ground Plane Antenna Calculator V0.1</b>: \
                                <br />This software calculates the distance that Ground Plane Antenna radials must have to transmit in the entered frequency. \
                                <br />by Renzo Ch.")
                                
  
def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = SisTeA_App()                 # We set the form to be our AntennaCalculatorApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                              # run the main function
