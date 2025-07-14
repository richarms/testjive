# testjive

Requirements:

Implement SDP-side receive of VDIF packets using jive5ab. Sub-tasks:

- Set up both machines for network throughput as per https://www.haystack.mit.edu/wp-content/uploads/2023/05/TOW12_SEM_Verkouter.pdf

- Stream simulated processed VDIF frames over UDP, simulating the output from the CBF V-engine. Make sure to adhere to https://vlbi.org/wp-content/uploads/2019/03/VDIF_specification_Release_1.1.1.pdf 

- Use jive5ab to record these data to disk using the Flexbuff format, simulating the SDP receive-side. Verify that these recorded files are valid for downstream transmission to a central facility and VLBI correlation.

- (if possible/ideally) configure/verify this simulated setup over multicast.

- Confirm that SDP can handle data at the maximum theoretical rate (initial: 2 * 32 MHz channels, goal: 2 * 64 MHz and 4 * 32 MHz S- and L-band)
