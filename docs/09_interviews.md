# Evidence of Relevance: Interviews & Public Reports

## 1. Research Approach and Constraints

Conducting direct, structured interviews with end-users (e.g., emergency services personnel or local authorities) was not feasible within the project's initial timeframe. The 2024 spring floods were a rapidly evolving emergency, and access to operational decision-makers during the disaster recovery phase was limited. 

To ensure the relevance of the project is still supported by verifiable evidence, this section relies on the analysis of public reports, official government statements, and witness accounts from the 2024 Kazakhstan floods. This approach helps validate the core problem statement and distinguishes verified findings from our initial assumptions.

## 2. Analysis of Public Reports and Official Statements

The relevance of the project—specifically the focus on *settlement isolation* rather than just water mapping—is strongly supported by the following verified facts from the 2024 flood event:

*   **Verified Finding 1: Widespread isolation of settlements.** 
    *   *Source:* BBC News and other international media reports covering the 2024 Kazakhstan floods.
    *   *Evidence:* Reports explicitly stated that over 60 settlements were completely cut off from external access due to floodwaters. This directly validates the project's core premise: emergency services need to know not just where the water is, but which communities are isolated.
*   **Verified Finding 2: Critical infrastructure damage.** 
    *   *Source:* Official statements from local authorities (e.g., Akimat of Atyrau Region).
    *   *Evidence:* Official data confirmed significant damage to transport infrastructure, including over 27.9 km of roads and 6 bridges destroyed or submerged in the Atyrau region alone. This confirms that road network disruption is a primary consequence of the floods, justifying the use of OpenStreetMap (OSM) road graphs for isolation assessment.
*   **Verified Finding 3: Delayed relief to isolated areas.** 
    *   *Source:* Witness accounts and news reports from affected regions (e.g., Kulsary).
    *   *Evidence:* Local residents reported that aid and rescue teams experienced severe difficulties reaching certain villages, as traditional access routes were flooded. This highlights the operational need for a rapid, automated tool that identifies isolation zones in near real-time.

## 3. Assumptions vs. Verified Findings

While the general problem is verified by public data, the specific technological requirements remain partially based on assumptions that require further validation:

*   **Assumption:** Emergency responders need a web platform specifically utilizing SAR (Synthetic Aperture Radar) data. 
    *   *Rationale:* SAR is chosen because it penetrates cloud cover, which is often present during floods. However, whether emergency services have the technical capacity to interpret SAR-based isolation maps without prior training remains an assumption to be tested.
*   **Assumption:** The primary bottleneck in current workflows is the manual threshold selection in flood mapping. 
    *   *Status:* This is supported by the academic literature review (e.g., Amoah, 2026; Khanh & Le, 2026), but its real-world operational impact needs confirmation from GIS analysts.

## 4. Conclusion

The literature and public reports confirm that during the 2024 floods in Kazakhstan, the disruption of the road network led to the isolation of numerous settlements, severely complicating rescue operations. The project directly addresses this verified problem by automating the detection of these isolated zones using SAR data and OSM road networks. The lack of formal interviews is a limitation, but the reliance on documented emergency events provides a robust foundation for the project's relevance.