'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Button } from 'primereact/button';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { MultiSelect } from 'primereact/multiselect';

interface FilterOption {
  name: string;
  code: string;
}

const SideBar = () => {
  const [selectedTypes, setSelectedTypes] = useState<FilterOption[]>([]);
  const [selectedTechniques, setSelectedTechniques] = useState<FilterOption[]>([]);
  const [selectedRatios, setSelectedRatios] = useState<FilterOption[]>([]);
  const [selectedTimeOfDay, setSelectedTimeOfDay] = useState<FilterOption[]>([]);
  const [selectedInteriorExterior, setSelectedInteriorExterior] = useState<FilterOption[]>([]);

  const typeOptions: FilterOption[] = [
    { name: 'Movie', code: 'movie' },
    { name: 'Music Video', code: 'musicvideo' },
    { name: 'Commercial', code: 'commercial' },
    { name: 'Short Film', code: 'short' },
  ];

  const techniqueOptions: FilterOption[] = [
    { name: 'Flash Cut', code: 'flashcut' },
    { name: 'Zoom Out', code: 'zoomout' },
    { name: 'Double Exposure', code: 'doubleexposure' },
    { name: 'Trail Printing', code: 'trailprinting' },
    { name: 'Accordion Blur', code: 'accordionblur' },
  ];

  const ratioOptions: FilterOption[] = [
    { name: '16:9', code: '16:9' },
    { name: '4:3', code: '4:3' },
    { name: '1:1', code: '1:1' },
    { name: '2.35:1', code: '2.35:1' },
  ];

  const timeOfDayOptions: FilterOption[] = [
    { name: 'Day', code: 'day' },
    { name: 'Night', code: 'night' },
    { name: 'Golden Hour', code: 'goldenhour' },
    { name: 'Blue Hour', code: 'bluehour' },
  ];

  const interiorExteriorOptions: FilterOption[] = [
    { name: 'Interior', code: 'interior' },
    { name: 'Exterior', code: 'exterior' },
  ];

  const panelTemplate = (options: {
    header: string;
    options: FilterOption[];
    value: FilterOption[];
    onChange: (e: { value: FilterOption[] }) => void;
  }) => {
    return (
      <AccordionTab header={options.header}>
        <MultiSelect
          value={options.value}
          options={options.options}
          onChange={options.onChange}
          optionLabel="name"
          display="chip"
          placeholder="Select options"
          className="w-full"
        />
      </AccordionTab>
    );
  };

  return (
    <div className="bg-[#121212] text-white h-full min-h-screen w-64 border-r border-[#2a2a2a]">
      <div className="p-4">
        <div className="text-gray-400 text-sm mb-2">Filter:</div>

        <Accordion multiple className="sidebar-accordion">
          {panelTemplate({
            header: 'Type',
            options: typeOptions,
            value: selectedTypes,
            onChange: (e) => setSelectedTypes(e.value),
          })}

          {panelTemplate({
            header: 'Technique',
            options: techniqueOptions,
            value: selectedTechniques,
            onChange: (e) => setSelectedTechniques(e.value),
          })}

          {panelTemplate({
            header: 'Frame size',
            options: ratioOptions,
            value: selectedRatios,
            onChange: (e) => setSelectedRatios(e.value),
          })}

          {panelTemplate({
            header: 'Time Of Day',
            options: timeOfDayOptions,
            value: selectedTimeOfDay,
            onChange: (e) => setSelectedTimeOfDay(e.value),
          })}

          {panelTemplate({
            header: 'Interior / Exterior',
            options: interiorExteriorOptions,
            value: selectedInteriorExterior,
            onChange: (e) => setSelectedInteriorExterior(e.value),
          })}

          <AccordionTab header="Characters">
            {/* Character filter content */}
          </AccordionTab>

          <AccordionTab header="Age">
            {/* Age filter content */}
          </AccordionTab>

          <AccordionTab header="Gender">
            {/* Gender filter content */}
          </AccordionTab>
        </Accordion>

        {(selectedTypes.length > 0 ||
          selectedTechniques.length > 0 ||
          selectedRatios.length > 0 ||
          selectedTimeOfDay.length > 0 ||
          selectedInteriorExterior.length > 0) && (
          <div className="mt-4 flex justify-end">
            <Button
              label="Clear All"
              icon="pi pi-times"
              className="p-button-text text-white text-sm"
              onClick={() => {
                setSelectedTypes([]);
                setSelectedTechniques([]);
                setSelectedRatios([]);
                setSelectedTimeOfDay([]);
                setSelectedInteriorExterior([]);
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default SideBar;
